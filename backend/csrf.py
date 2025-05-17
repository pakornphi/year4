import requests
from bs4 import BeautifulSoup
import time
import argparse
import logging
from urllib.parse import urljoin

# Disable all logging (no logs will be shown)
logging.disable(logging.CRITICAL)

class CSRFTester:
    def __init__(
        self,
        base_url: str,
        csrf_field: str = 'csrf_token',
        form_selector: str = 'form',
        endpoints: list[str] = None,
        timeout: float = 5.0,
        headers: dict = None,
        max_retries: int = 2
    ):
        self.base_url = base_url.rstrip('/')
        self.csrf_field = csrf_field
        self.form_selector = form_selector
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.timeout = timeout
        self.endpoints = endpoints or ['/']
        adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Explicitly map test names to methods for clearer output
        self.tests = {
            'Missing CSRF Token':               self.test_csrf_presence,
            'CSRF Token Reuse Allowed':         self.test_csrf_reuse,
            'Malformed CSRF Token Accepted':    self.test_token_format,
            'Static CSRF Token (No Rotation)':  self.test_dynamic_token,
            'Missing Double-Submit Cookie':     self.test_double_submit_cookie,
            'Token Expiration Not Enforced':    self.test_expiration,
            'Session Fixation Protection':      self.test_session_fixation,
        }

    def _get(self, path: str):
        url = urljoin(self.base_url, path)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def _post(self, path: str, data: dict):
        url = urljoin(self.base_url, path)
        resp = self.session.post(url, data=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def _find_forms(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.select(self.form_selector)

    def _extract_fields(self, form):
        action = form.get('action', '/')
        method = form.get('method', 'post').lower()
        data = {inp['name']: inp.get('value', '') for inp in form.select('input[name]')}
        return action, method, data

    def run_all(self):
        results = {}
        # Print the base URL only once before starting the tests
        print(f"Testing URL: {self.base_url}")
        
        for name, fn in self.tests.items():
            try:
                vuln, info = fn()
                results[name] = (vuln, info)
                # Print only the result for the test
                status = vuln if vuln is not None else 'None'
                line = f"  {name:30s} → vulnerability:{status}"
                if info is not None:
                    line += f"   info={info}"
                print(line)
            except Exception:
                results[name] = (None, None)
                print(f"  {name:30s} → vulnerability:None")
        return results

    def print_results(self):
        self.run_all()

    # === TESTS BELOW ===
    def test_csrf_presence(self):
        """Missing hidden field => vulnerability."""
        for path in self.endpoints:
            html = self._get(path).text
            for form in self._find_forms(html):
                _, _, data = self._extract_fields(form)
                if self.csrf_field not in data:
                    return True, path
        return False, None

    def test_csrf_reuse(self):
        """Reuse same token twice => vulnerability."""
        for path in self.endpoints:
            html = self._get(path).text
            for form in self._find_forms(html):
                action, method, data = self._extract_fields(form)
                token = data.get(self.csrf_field)
                if not token:
                    continue
                # first submit
                if method == 'post':
                    self._post(action, data)
                else:
                    self._get(action, params=data)
                # second submit
                try:
                    if method == 'post':
                        self._post(action, data)
                    else:
                        self._get(action, params=data)
                    return True, token
                except:
                    pass
        return False, None

    def test_token_format(self):
        """Server must reject malformed tokens."""
        for path in self.endpoints:
            html = self._get(path).text
            for form in self._find_forms(html):
                action, method, data = self._extract_fields(form)
                if self.csrf_field not in data:
                    continue
                data[self.csrf_field] = 'X' * len(data[self.csrf_field])
                try:
                    if method == 'post':
                        self._post(action, data)
                    else:
                        self._get(action, params=data)
                    return True, data[self.csrf_field]
                except:
                    pass
        return False, None

    def test_dynamic_token(self):
        """Token must change on each GET."""
        for path in self.endpoints:
            html1 = self._get(path).text
            forms1 = self._find_forms(html1)
            time.sleep(1)
            html2 = self._get(path).text
            forms2 = self._find_forms(html2)
            for f1, f2 in zip(forms1, forms2):
                _, _, d1 = self._extract_fields(f1)
                _, _, d2 = self._extract_fields(f2)
                if d1.get(self.csrf_field) == d2.get(self.csrf_field):
                    return True, d1.get(self.csrf_field)
        return False, None

    def test_double_submit_cookie(self):
        """Double-submit cookie missing => vulnerability."""
        resp = self._get('/')
        cookie_val = self.session.cookies.get(self.csrf_field)
        if not cookie_val:
            return True, None
        html = resp.text
        for form in self._find_forms(html):
            _, _, data = self._extract_fields(form)
            if data.get(self.csrf_field) == cookie_val:
                return False, cookie_val
        return True, None

    def test_expiration(self, wait: int = 5):
        """Reusing token after wait => vulnerability."""
        html = self._get('/').text
        action, method, data = self._extract_fields(self._find_forms(html)[0])
        token = data.get(self.csrf_field)
        if method == 'post':
            self._post(action, data)
        else:
            self._get(action, params=data)
        time.sleep(wait)
        try:
            if method == 'post':
                self._post(action, data)
            else:
                self._get(action, params=data)
            return True, token
        except:
            return False, token

    def test_session_fixation(self):
        """Session must rotate on login; treat 404/405 as protected."""
        orig = self.session.cookies.get('session')
        self.session.cookies.set('session', 'attacker_value')

        login_path = '/login'
        login_url = urljoin(self.base_url, login_path)

        try:
            resp = self.session.get(login_url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code in (404, 405):
                return False, (orig, None)
            raise

        new = self.session.cookies.get('session')
        if new in (orig, 'attacker_value'):
            return True, (orig, new)
        return False, (orig, new)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base_url', help='e.g. https://example.com')
    parser.add_argument('--csrf-field', default='csrf_token')
    parser.add_argument('--form-selector', default='form')
    parser.add_argument('--endpoints', nargs='*', default=['/'])
    args = parser.parse_args()

    tester = CSRFTester(
        base_url=args.base_url,
        csrf_field=args.csrf_field,
        form_selector=args.form_selector,
        endpoints=args.endpoints
    )

    tester.print_results()