import argparse
import inspect
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class XSSTester:
    def __init__(
        self,
        base_url,
        timeout=5,
        cooldown=1,
        max_redirects=0,
        workers=5
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cooldown = cooldown
        self.workers = workers
        self._soup_cache = {}

        # Always read payloads from 'payload.txt' (fixed file)
        self.payloads = self._read_payloads('payload.txt')

        logging.info(f"Loaded {len(self.payloads)} payloads from 'payload.txt'")

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
        """
        Reads a list of payloads from the specified file.
        Assumes the file contains a list of payloads (one per line).
        """
        payloads = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                raise ValueError(f"The payload file '{path}' is empty or invalid.")
        except FileNotFoundError:
            logging.error(f"Payload file '{path}' not found.")
            raise
        except Exception as e:
            logging.error(f"Error reading payloads from '{path}': {e}")
            raise
        return payloads

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
        # Cache by URL to avoid repeated fetches
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
            test_qs = qs.copy()
            test_qs[p] = [self.payload]
            url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                '',
                urlencode(test_qs, doseq=True),
                ''
            ))
            resp = self._get(url, allow_redirects=False)
            if self.payload in getattr(resp, 'text', ''):
                return {'vulnerability': True, 'payload': self.payload}
    
        return {'vulnerability': False}

    def test_form_input_xss(self):
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            action_url = urlparse(self.base_url)._replace(path=action).geturl()
            data = {
                inp.get('name'): (self.payload if inp.get('type', 'text') in ['text', 'search', 'email', 'url']
                                  else inp.get('value', ''))
                for inp in form.find_all('input') if inp.get('name')
            }
            resp = self._post(action_url, data=data) if form.get('method', 'get').lower() == 'post' else self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                return {'vulnerability': True, 'payload': self.payload}
        return {'vulnerability': False}

    def test_header_xss(self):
        headers = {'User-Agent': self.payload}
        resp = self._get(self.base_url, headers=headers)
        if self.payload in getattr(resp, 'text', ''):
            return {'vulnerability': True, 'payload': self.payload}
        return {'vulnerability': False}

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
            resp = self._post(action_url, data=data) if form.get('method', 'get').lower() == 'post' else self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                return {'vulnerability': True, 'payload': self.payload}
        return {'vulnerability': False}

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
            resp = self._post(action_url, data=data) if form.get('method', 'get').lower() == 'post' else self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                return {'vulnerability': True, 'payload': self.payload}
        return {'vulnerability': False}

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
            resp = self._post(action_url, data=data, files=files) if form.get('method', 'get').lower() == 'post' else self._get(action_url, params=data)
            if self.payload in getattr(resp, 'text', ''):
                return {'vulnerability': True, 'payload': self.payload}
        return {'vulnerability': False}

    def _run_single(self, method, payload):
        self.payload = payload
        return method()

    def run_all(self, max_workers=None):
        results = {}
        methods = [
            (name, m) for name, m in inspect.getmembers(self, inspect.ismethod)
            if name.startswith('test_')
        ]
        workers = max_workers or self.workers

        for name, method in methods:
            result = []
            # Submit each payload test to the ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(self._run_single, method, p): p for p in self.payloads}
                for future in as_completed(futures):
                    res = future.result()  # Get the result from the future
                    if isinstance(res, dict):
                        result.append(res)  # If the result is a dictionary, append it
                    else:
                        # If the result is a boolean, treat it as a dictionary
                        result.append({'vulnerability': res})

            results[name] = result

        return results

    def print_results(self, results):
        printed_tests = set()  # Keep track of printed tests to avoid duplicates
        
        # Iterate over all tests and their results
        for test, result_list in results.items():
            for result in result_list:
                if isinstance(result, dict):
                    vulnerability = result['vulnerability']
                    payload = result.get('payload', 'N/A')
                    
                    # Construct the result string for the test
                    result_str = f"{test} → vulnerability: {vulnerability}"

                    # If the vulnerability is True, include the payload
                    if vulnerability == True:
                        result_str += f" with payload: {payload}"

                    # Ensure no duplicate results are printed
                    if result_str not in printed_tests:
                        print(result_str)  # Print the result if not printed before
                        printed_tests.add(result_str)  # Add to the set of printed results


def main():
    parser = argparse.ArgumentParser(description="XSS Testing Script")
    parser.add_argument('url', help="Base URL to test, including any query string")
    parser.add_argument('--timeout', type=int, default=3, help="HTTP timeout in seconds")
    parser.add_argument('--cooldown', type=float, default=0.5, help="Cooldown between requests in seconds")
    parser.add_argument('--workers', type=int, default=10, help="Number of parallel worker threads")
    args = parser.parse_args()

    tester = XSSTester(
        base_url=args.url,
        timeout=args.timeout,
        cooldown=args.cooldown,
        workers=args.workers
    )
    results = tester.run_all(max_workers=args.workers)
    tester.print_results(results)


if __name__ == '__main__':
    main()
