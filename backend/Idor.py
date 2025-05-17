# idor_improved.py
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

COMMON_PARAMS = ["id", "user_id", "account", "order_id", "file"]

class IDORSummarizedTester:
    def __init__(self, url, start=1, end=5, timeout=5):
        self.url = url
        self.start = start
        self.end = end
        self.timeout = timeout
        self.session = requests.Session()

        # Descriptive names for each parameter
        self.descriptive_names = {
            'id': 'ID parameter',
            'user_id': 'User ID parameter',
            'account': 'Account parameter',
            'order_id': 'Order ID parameter',
            'file': 'File parameter'
        }

    def _modify_url(self, param, value):
        parsed = urlparse(self.url)
        query = parse_qs(parsed.query)
        query[param] = [str(value)]
        new_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def _base_request(self):
        resp = self.session.get(self.url, timeout=self.timeout)
        return resp.status_code, resp.text.strip()

    def _test_param(self, param):
        base_status, base_text = self._base_request()
        for val in range(self.start, self.end + 1):
            test_url = self._modify_url(param, val)
            try:
                resp = self.session.get(test_url, timeout=self.timeout)
                if resp.status_code != base_status or resp.text.strip() != base_text:
                    return True
            except Exception:
                return True  # Error implies potential issue
        return False

    def run_all(self):
        results = {}
        print(f"Testing URL: {self.url}")
        for param in COMMON_PARAMS:
            vuln = self._test_param(param)
            # Determine label based on vulnerability
            name = self.descriptive_names.get(param, param)
            if vuln:
                label = f"{name} insecure"
            else:
                label = f"{name} secure"

            status = 'True' if vuln else 'False'
            print(f"  {label:30s} → vulnerability:{status}")
            results[param] = vuln
        return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Summarized IDOR Tester')
    parser.add_argument('url', help='Target URL with query parameter to test')
    parser.add_argument('--start', type=int, default=1, help='Start of ID range')
    parser.add_argument('--end', type=int, default=5, help='End of ID range')
    parser.add_argument('--timeout', type=float, default=5.0, help='Request timeout in seconds')
    args = parser.parse_args()

    tester = IDORSummarizedTester(
        url=args.url,
        start=args.start,
        end=args.end,
        timeout=args.timeout
    )
    tester.run_all()
