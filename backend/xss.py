# xss_tester_improved.py

import argparse
import logging
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class XSSTester:
    """
    XSS testing toolkit that reads its payloads from Python files,
    caches fetched pages, and runs tests in parallel.

    Outputs results in a uniform format:
        Testing URL: <base_url>
          Test Name                  → vulnerability:<True/False>   count=<int>
    """

    def __init__(self, base_url, payload_file, timeout=5, cooldown=1, workers=5):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cooldown = cooldown
        self.workers = workers
        self._soup_cache = {}

        # Load generic payloads
        namespace = {}
        with open(payload_file, 'r', encoding='utf-8') as f:
            exec(f.read(), namespace)
        if 'PAYLOADS' not in namespace:
            raise AttributeError(f"No PAYLOADS list found in {payload_file}")
        self.payloads = namespace['PAYLOADS']

        logging.info(f"Loaded {len(self.payloads)} payloads from '{payload_file}'")

        # Configure HTTP session
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=workers,
            pool_maxsize=workers
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Map descriptive test names to methods
        self.tests = {
            'Query Parameter XSS': self.test_query_parameter_xss,
            'Form Input XSS':      self.test_form_input_xss,
            'Header XSS':          self.test_header_xss,
            'Comment Field XSS':   self.test_comment_xss,
            'Profile Field XSS':   self.test_profile_field_xss,
            'File Upload XSS':     self.test_file_upload_xss,
        }

    def _sleep(self):
        time.sleep(self.cooldown)

    def _get(self, url, **kwargs):
        try:
            return self.session.get(url, timeout=self.timeout, **kwargs)
        except requests.RequestException:
            return type('r', (), {'text': '', 'status_code': None})()
        finally:
            self._sleep()

    def _post(self, url, **kwargs):
        try:
            return self.session.post(url, timeout=self.timeout, **kwargs)
        except requests.RequestException:
            return type('r', (), {'text': '', 'status_code': None})()
        finally:
            self._sleep()

    def _fetch_soup(self, url):
        if url in self._soup_cache:
            return self._soup_cache[url]
        resp = self._get(url)
        soup = BeautifulSoup(resp.text or '', 'html.parser')
        self._soup_cache[url] = soup
        return soup

    def test_query_parameter_xss(self):
        count = 0
        parsed = urlparse(self.base_url)
        qs = parse_qs(parsed.query)
        params = list(qs) or ['q']
        for p in params:
            for payload in self.payloads:
                test_qs = {k: (payload if k == p else v[0]) for k, v in qs.items()} if qs else {p: payload}
                url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', urlencode(test_qs), ''))
                resp = self._get(url)
                if payload in resp.text:
                    count += 1
        return count

    def test_form_input_xss(self):
        count = 0
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            for payload in self.payloads:
                data = {inp.get('name'): payload for inp in form.find_all('input') if inp.get('name')}
                if form.get('method', 'get').lower() == 'post':
                    resp = self._post(action, data=data)
                else:
                    resp = self._get(action, params=data)
                if payload in resp.text:
                    count += 1
        return count

    def test_header_xss(self):
        count = 0
        for payload in self.payloads:
            resp = self._get(self.base_url, headers={'User-Agent': payload})
            if payload in resp.text:
                count += 1
        return count

    def test_comment_xss(self):
        count = 0
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            for payload in self.payloads:
                data = {field.get('name'): payload if 'comment' in field.get('name', '').lower() else field.get('value', '')
                        for field in form.find_all(['input', 'textarea']) if field.get('name')}
                if form.get('method', 'get').lower() == 'post':
                    resp = self._post(action, data=data)
                else:
                    resp = self._get(action, params=data)
                if payload in resp.text:
                    count += 1
        return count

    def test_profile_field_xss(self):
        count = 0
        keys = ['profile', 'bio', 'about', 'description']
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            for payload in self.payloads:
                data = {field.get('name'): payload if any(k in field.get('name', '').lower() for k in keys) else field.get('value', '')
                        for field in form.find_all(['input', 'textarea']) if field.get('name')}
                if form.get('method', 'get').lower() == 'post':
                    resp = self._post(action, data=data)
                else:
                    resp = self._get(action, params=data)
                if payload in resp.text:
                    count += 1
        return count

    def test_file_upload_xss(self):
        count = 0
        soup = self._fetch_soup(self.base_url)
        for form in soup.find_all('form'):
            action = form.get('action') or self.base_url
            file_inputs = form.find_all('input', {'type': 'file'})
            if not file_inputs:
                continue
            for payload in self.payloads:
                data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name') and inp.get('type') != 'file'}
                files = {fi.get('name'): ('payload.html', payload, 'text/html') for fi in file_inputs if fi.get('name')}
                if form.get('method', 'get').lower() == 'post':
                    resp = self._post(action, data=data, files=files)
                else:
                    resp = self._get(action, params=data)
                if payload in resp.text:
                    count += 1
        return count

    def run_all(self):
        print(f"Testing URL: {self.base_url}")
        for name, fn in self.tests.items():
            count = fn()
            vulnerable = count > 0
            status = 'True' if vulnerable else 'False'
            print(f"  {name:30s} → vulnerability:{status}   count={count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="XSS Testing Script")
    parser.add_argument('url', help="Base URL to test, including any query string")
    parser.add_argument('--payload-file', '-f', required=True, help="Path to payload file (defines PAYLOADS list)")
    parser.add_argument('--timeout', type=int, default=3, help="HTTP timeout in seconds")
    parser.add_argument('--cooldown', type=float, default=0.5, help="Cooldown between requests in seconds")
    parser.add_argument('--workers', type=int, default=5, help="Number of parallel worker threads")
    args = parser.parse_args()

    tester = XSSTester(
        base_url=args.url,
        payload_file=args.payload_file,
        timeout=args.timeout,
        cooldown=args.cooldown,
        workers=args.workers
    )
    tester.run_all()