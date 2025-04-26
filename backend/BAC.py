import requests
import re
from urllib.parse import urljoin

class BrokenAccessControlTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "AccessControlTester/1.0"}
        self.json_headers = {**self.headers, "Content-Type": "application/json"}

    def _report(self, vulnerable, action, path, code):
        status = "[PASS]" if vulnerable else "[FAILED]"
        note = "❗ Vulnerable" if vulnerable else "✅ Protected"
        print(f"{status} {action} {self.base_url + path} (HTTP {code}) {note}")

    def test_admin_panel(self, paths=None):
        """Test Case 2: URL Access to Admin Panel"""
        if paths is None:
            paths = ["/admin", "/dashboard/admin", "/manage", "/admin/users", "/admin-panel"]
        print("\n=== Test Case 2: Admin Panel Access ===")
        for p in paths:
            try:
                r = requests.get(self.base_url + p, headers=self.headers, allow_redirects=False)
                vulnerable = (r.status_code == 200)
                self._report(vulnerable, "GET", p, r.status_code)
            except Exception as e:
                print(f"[ERROR] GET {self.base_url + p}: {e}")

    def test_http_methods(self, endpoints=None, payload=None):
        """Test Case 3: Privilege Escalation via HTTP Methods"""
        if endpoints is None:
            endpoints = ["/api/users/1", "/api/posts/10", "/admin/settings"]
        if payload is None:
            payload = {"role": "admin", "username": "hacker"}

        print("\n=== Test Case 3: HTTP Methods Privilege Escalation ===")
        for ep in endpoints:
            full = self.base_url + ep

            # PUT
            try:
                r_put = requests.put(full, json=payload, headers=self.json_headers)
                self._report(r_put.status_code in (200,201,204), "PUT", ep, r_put.status_code)
            except Exception as e:
                print(f"[ERROR] PUT {full}: {e}")

            # DELETE
            try:
                r_del = requests.delete(full, headers=self.headers)
                self._report(r_del.status_code in (200,202,204), "DELETE", ep, r_del.status_code)
            except Exception as e:
                print(f"[ERROR] DELETE {full}: {e}")

    def test_role_bypass(self, path="/admin", fake_header_key="X-Role", fake_cookie_key="role"):
        """Test Case 4: Bypass Role-Based Access via Cookies/Headers"""
        print("\n=== Test Case 4: Role Bypass ===")
        cookies = {fake_cookie_key: "admin"}
        headers = {**self.headers, fake_header_key: "admin"}
        try:
            r = requests.get(self.base_url + path, headers=headers, cookies=cookies, allow_redirects=False)
            self._report(r.status_code == 200, "GET with forged role", path, r.status_code)
        except Exception as e:
            print(f"[ERROR] Role bypass {self.base_url + path}: {e}")

    def test_hidden_functions(self):
        """Test Case 5: Access Hidden Functions via JS Discovery"""
        print("\n=== Test Case 5: Hidden JS Endpoints ===")
        # 1) discover JS files
        try:
            home = requests.get(self.base_url, headers=self.headers).text
        except Exception as e:
            return print(f"[ERROR] Fetch main page: {e}")

        js_files = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', home)
        js_urls = [urljoin(self.base_url, src) for src in js_files]
        print(f"Discovered {len(js_urls)} JS files.")

        # 2) extract endpoints and test
        endpoints = set()
        for js in js_urls:
            try:
                content = requests.get(js, headers=self.headers).text
                found = re.findall(r'["\'](\/[A-Za-z0-9_\-/]+?)["\']', content)
                endpoints.update(found)
            except Exception as e:
                print(f"[ERROR] Fetch JS {js}: {e}")

        print(f"Testing {len(endpoints)} endpoints:")
        for ep in sorted(endpoints):
            try:
                r = requests.get(self.base_url + ep, headers=self.headers, allow_redirects=False)
                self._report(r.status_code == 200, "GET hidden", ep, r.status_code)
            except Exception as e:
                print(f"[ERROR] GET {self.base_url + ep}: {e}")

    def run_all(self):
        """Run all test cases in sequence."""
        self.test_admin_panel()
        self.test_http_methods()
        self.test_role_bypass()
        self.test_hidden_functions()


if __name__ == "__main__":
    tester = BrokenAccessControlTester("http://localhost:8000")
    tester.run_all()
