import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CSRFTester:
    def __init__(self, target_url, form_data=None, csrf_token_name='csrf_token'):
        """
        Initializer for CSRFTester class.
        :param target_url: Target URL for the test.
        :param form_data: Optional dictionary to override default form data.
        :param csrf_token_name: Optional custom name for CSRF token field (default: 'csrf_token').
        """
        self.target_url = target_url
        self.session = requests.Session()
        self.form_data = form_data or {'username': 'testuser', 'password': 'testpassword'}
        self.csrf_token_name = csrf_token_name
        self.results = []  # To store the test results

    def get_csrf_token(self):
        """Fetch the CSRF token from the target URL"""
        try:
            response = self.session.get(self.target_url)
            response.raise_for_status()  # Raise an exception if there is an HTTP error
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the CSRF token from the page
            csrf_token = self._extract_csrf_token(soup)
            form_tag = soup.find('form')
            form_action = urljoin(self.target_url, form_tag['action']) if form_tag else None
            method = form_tag.get('method', 'POST').upper() if form_tag else 'POST'

            return csrf_token, form_action, method

        except Exception as e:
            return None, None, None

    def _extract_csrf_token(self, soup):
        """Extract the CSRF token from HTML"""
        token_tag = soup.find('meta', {'name': 'csrf-token'})
        if token_tag:
            return token_tag.get('content')

        form_tag = soup.find('form')
        if form_tag:
            csrf_token_input = form_tag.find('input', {'name': self.csrf_token_name})
            if csrf_token_input:
                return csrf_token_input['value']

        return None

    def submit_form(self, form_action, data, method):
        """Submit the form with the given method (POST, PUT, PATCH)"""
        try:
            form_action = urljoin(self.target_url, form_action)
            response = None

            # Map the HTTP methods to corresponding requests
            http_methods = {
                'POST': self.session.post,
                'PUT': self.session.put,
                'PATCH': self.session.patch,
            }

            if method in http_methods:
                response = http_methods[method](form_action, data=data)
            else:
                self.results.append(f"Error: HTTP Method {method} not supported")
                return None

            return response

        except requests.exceptions.HTTPError as err:
            self.results.append(f"HTTP Error: {err}")
            return None

    def check_csrf_protection(self, response, expected_error_message="invalid request"):
        """Check if CSRF protection is working correctly"""
        if response is None:
            self.results.append("Response is None, cannot check")
            return

        # Check for HTTP 400 (Bad Request) response indicating CSRF protection is working
        if response.status_code == 400:
            self.results.append("CSRF protection successful: cannot submit without CSRF token")

        elif expected_error_message in response.text.lower():
            self.results.append(f"CSRF protection failed: {expected_error_message} - able to submit without CSRF token")

        elif response.status_code == 200 and "token reuse" not in response.text.lower():
            self.results.append("CSRF protection failed: able to submit using CSRF token")

        elif "token reuse" in response.text.lower() or "csrf token has expired" in response.text.lower():
            self.results.append("CSRF protection failed: able to submit using reused or expired token")

        else:
            self.results.append("CSRF protection failed: able to submit without CSRF token")

    def test_token_reuse(self):
        """Test the reuse of CSRF token"""
        csrf_token, form_action, method = self.get_csrf_token()

        if not form_action:
            self.results.append("Error: Form action not found")
            return

        form_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'csrf_token': csrf_token
        }

        response_1 = self.submit_form(form_action, form_data, method)
        
        if response_1 and response_1.status_code == 200:
            self.results.append("CSRF protection failed: able to submit with reused CSRF token")
        else:
            self.results.append("CSRF protection successful: cannot submit with reused CSRF token")

    def perform_test(self):
        """Main function to perform the CSRF test"""
        self.results.append(f"Starting CSRF test for: {self.target_url}")

        csrf_token, form_action, method = self.get_csrf_token()

        if not form_action:
            self.results.append("Error: Form action not found")
            return self.results

        form_data = self.form_data.copy()

        if csrf_token:
            self.results.append("CSRF token found")
            form_data.pop('csrf_token', None)
            response_no_csrf = self.submit_form(form_action, form_data, method)
            self.check_csrf_protection(response_no_csrf)

            # Test token reuse
            self.test_token_reuse()

        else:
            self.results.append("Error: CSRF token not found")
            form_data.pop('csrf_token', None)
            response_no_csrf = self.submit_form(form_action, form_data, method)
            self.check_csrf_protection(response_no_csrf)

            # Test token reuse
            self.test_token_reuse()

        return self.results