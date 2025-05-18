import argparse
import inspect
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class XSSTester:
    """
    XSS testing toolkit that reads its payloads from Python files or a provided list,
    caches fetched pages, and runs tests in parallel.
    """
    def __init__(
        self,
        base_url: str,
        payload_file: str = None,
        payloads: list[str] = None,
        timeout: float = 5,
        cooldown: float = 1,
        max_redirects: int = 0,
        workers: int = 5
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cooldown = cooldown
        self.workers = workers
        self._soup_cache = {}

        # Allow either a direct list or a file on disk
        if payloads is not None:
            self.payloads = payloads
            logging.info(f"Loaded {len(self.payloads)} payloads from provided list")
        elif payload_file:
            self.payloads = self._read_payloads(payload_file)
            logging.info(f"Loaded {len(self.payloads)} payloads from '{payload_file}'")
        else:
            self.payloads = []
            logging.info("No payloads provided; running with an empty list")

        # Load DOM-specific payloads from 'payloaddom.txt'
        self.dom_payloads = self._read_payloads('payloaddom.txt')
        logging.info(f"Loaded {len(self.dom_payloads)} DOM payloads from 'payloaddom.txt'")

        # Configure session with increased pool size
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=1,
            pool_connections=workers,
            pool_maxsize=workers
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.max_redirects = max_redirects

    def _read_payloads(self, path):
        namespace = {}
        if not path:
            return []
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        exec(code, namespace)
        if 'PAYLOADS' not in namespace:
            raise AttributeError(f"No PAYLOADS list found in {path}")
        return namespace['PAYLOADS']

    def _sleep(self):
        time.sleep(self.cooldown)

    def _get(self, url, **kwargs):
        try:
            return self.session.get(url, timeout=self.timeout, **kwargs)
        except requests.RequestException as e:
            logging.warning(f"GET request failed for {url}: {e}")
            return type('r', (), {'text': '', 'status_code': None})()
        finally:
            self._sleep()

    def _post(self, url, **kwargs):
        try:
            return self.session.post(url, timeout=self.timeout, **kwargs)
        except requests.RequestException as e:
            logging.warning(f"POST request failed for {url}: {e}")
            return type('r', (), {'text': '', 'status_code': None})()
        finally:
            self._sleep()

    def _fetch_soup(self, url):
        if url in self._soup_cache:
            return self._soup_cache[url]
        try:
            resp = self._get(url, allow_redirects=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            logging.warning(f"_fetch_soup failed for {url}: {e}")
            soup = BeautifulSoup('', 'html.parser')
        self._soup_cache[url] = soup
        return soup

    def test_query_parameter_xss(self):
        parsed = urlparse(self.base_url)
        qs = parse_qs(parsed.query)
        params = list(qs) or ['q']
        for p in params:
            test_qs = {k: (self.payload if k == p else v[0])
                       for k, v in qs.items()} if qs else {p: self.payload}
            url = urlunparse((parsed.scheme, parsed.netloc,
                              parsed.path, '', urlencode(test_qs), ''))
            resp = self._get(url, allow_redirects=False)
            if self.payload in getattr(resp, 'text', ''):
                logging.warning(f"query_parameter_xss vulnerable on: {p}")
                return True
        return False

    def test_form_input_xss(self):
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            action_url = urlparse(self.base_url)._replace(path=action).geturl()
            data = {
                inp.get('name'):
                (self.payload if inp.get('type', 'text') in ['text', 'search', 'email', 'url']
                 else inp.get('value', ''))
                for inp in form.find_all('input') if inp.get('name')
            }
            if form.get('method', 'get').lower() == 'post':
                resp = self._post(action_url, data=data)
            else:
                resp = self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                logging.warning(f"form_input_xss vulnerable on: {action_url}")
                return True
        return False

    def test_header_xss(self):
        headers = {'User-Agent': self.payload}
        resp = self._get(self.base_url, headers=headers)
        if self.payload in getattr(resp, 'text', ''):
            logging.warning("header_xss via User-Agent header")
            return True
        return False

    def test_comment_xss(self):
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            action_url = urlparse(self.base_url)._replace(path=action).geturl()
            data, found = {}, False
            for field in form.find_all(['input', 'textarea']):
                name = field.get('name')
                if not name:
                    continue
                if 'comment' in name.lower():
                    data[name] = self.payload
                    found = True
                else:
                    data[name] = (field.get('value', '') if field.name == 'input' else field.text)
            if not found:
                continue
            if form.get('method', 'get').lower() == 'post':
                resp = self._post(action_url, data=data)
            else:
                resp = self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                logging.warning(f"comment_xss vulnerable on: {action_url}")
                return True
        return False

    def test_profile_field_xss(self):
        keys = ['profile', 'bio', 'about', 'description']
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            action_url = urlparse(self.base_url)._replace(path=action).geturl()
            data, found = {}, False
            for field in form.find_all(['input', 'textarea']):
                name = field.get('name')
                if not name:
                    continue
                if any(k in name.lower() for k in keys):
                    data[name] = self.payload
                    found = True
                else:
                    data[name] = (field.get('value', '') if field.name == 'input' else field.text)
            if not found:
                continue
            if form.get('method', 'get').lower() == 'post':
                resp = self._post(action_url, data=data)
            else:
                resp = self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                logging.warning(f"profile_field_xss vulnerable on: {action_url}")
                return True
        return False

    def test_file_upload_xss(self):
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            action_url = urlparse(self.base_url)._replace(path=action).geturl()
            file_inputs = form.find_all('input', {'type': 'file'})
            if not file_inputs:
                continue
            data = {
                inp.get('name'): inp.get('value', '')
                for inp in form.find_all('input')
                if inp.get('name') and inp.get('type') != 'file'
            }
            files = {
                fi.get('name'): ('payload.html', self.payload, 'text/html')
                for fi in file_inputs if fi.get('name')
            }
            if form.get('method', 'get').lower() == 'post':
                resp = self._post(action_url, data=data, files=files)
            else:
                resp = self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                logging.warning(f"file_upload_xss vulnerable on: {action_url}")
                return True
        return False

    def _run_single(self, method, payload):
        self.payload = payload
        return method()

    def run_all(self, max_workers=None) -> dict:
        """
        Run each test_* method in parallel across payloads, then
        return a dict mapping each test name to the list of successful payloads.
        """
        results = {}
        methods = [
            (name, m) for name, m in inspect.getmembers(self, inspect.ismethod)
            if name.startswith('test_') and name != 'test_dom_xss'
        ]
        workers = max_workers or self.workers

        for name, method in methods:
            vulnerable = []
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(self._run_single, method, p): p
                           for p in self.payloads}
                for future in as_completed(futures):
                    if future.result():
                        vulnerable.append(futures[future])

            logging.info(f"{name}: {len(vulnerable)} payloads triggered vulnerability")
            results[name] = vulnerable

        results['vulnerability'] = any(
            results[test] for test in results if test != 'vulnerability'
        )

        # Format and return the summary string
        return results

    def print_results(self, results):
        """
        Display the formatted summary (same as run_all() returns).
        """
        print(self._format_results(results))

    def _format_results(self, results) -> str:
        """
        Build and return the multi-line summary report.
        """
        lines = [f"Testing URL: {self.base_url}"]
        tests = [
            ('test_query_parameter_xss', 'Query Parameter XSS'),
            ('test_form_input_xss',      'Form Input XSS'),
            ('test_header_xss',          'Header XSS'),
            ('test_comment_xss',         'Comment Field XSS'),
            ('test_profile_field_xss',   'Profile Field XSS'),
            ('test_file_upload_xss',     'File Upload XSS'),
        ]
        for key, label in tests:
            vuln_list = results.get(key, [])
            status = 'True' if vuln_list else 'False'
            count = len(vuln_list)
            lines.append(f"  {label:<28} → vulnerability:{status:<5} count={count}")
        return "\n".join(lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="XSS Testing Script")
    parser.add_argument('url', help="Base URL to test, including any query string")
    parser.add_argument('--payload-file', '-f', required=True,
                        help="Path to payload file (defines PAYLOADS list)")
    parser.add_argument('--timeout', type=int, default=3,
                        help="HTTP timeout in seconds")
    parser.add_argument('--cooldown', type=float, default=0.5,
                        help="Cooldown between requests in seconds")
    parser.add_argument('--workers', type=int, default=10,
                        help="Number of parallel worker threads")
    args = parser.parse_args()

    tester = XSSTester(
        base_url=args.url,
        payload_file=args.payload_file,
        timeout=args.timeout,
        cooldown=args.cooldown,
        workers=args.workers
    )
    summary = tester.run_all(max_workers=args.workers)
    print(summary)