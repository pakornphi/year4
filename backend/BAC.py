import requests
import re
from urllib.parse import urljoin

class BrokenAccessControlTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "AccessControlTester/1.0"}
        self.json_headers = {**self.headers, "Content-Type": "application/json"}
        
        # Store test methods in a dictionary
        self.tests = {
            'Admin Panel Access': self.test_admin_panel,
            'HTTP Methods Privilege Escalation': self.test_http_methods,
            'Role Bypass': self.test_role_bypass,
            'Hidden JS Endpoints': self.test_hidden_functions
        }

    def test_admin_panel(self, paths=None):
        """Test Case 2: URL Access to Admin Panel"""
        if paths is None:
            paths = ["/admin", "/dashboard/admin", "/manage", "/admin/users", "/admin-panel"]
        print("\n=== Test Case 2: Admin Panel Access ===")
        results = []
        for p in paths:
            try:
                r = requests.get(self.base_url + p, headers=self.headers, allow_redirects=False)
                vulnerable = (r.status_code == 200)  # Vulnerable if status 200 is returned
                results.append((vulnerable, f"GET {p}: {r.status_code}"))
            except Exception as e:
                print(f"[ERROR] GET {self.base_url + p}: {e}")
                results.append((None, f"GET {p}: Error"))
        return results

    def test_http_methods(self, endpoints=None, payload=None):
        """Test Case 3: Privilege Escalation via HTTP Methods"""
        if endpoints is None:
            endpoints = ["/api/users/1", "/api/posts/10", "/admin/settings"]
        if payload is None:
            payload = {"role": "admin", "username": "hacker"}

        print("\n=== Test Case 3: HTTP Methods Privilege Escalation ===")
        results = []
        for ep in endpoints:
            full = self.base_url + ep

            # PUT
            try:
                r_put = requests.put(full, json=payload, headers=self.json_headers)
                results.append((r_put.status_code in (200, 201, 204), f"PUT {ep}: {r_put.status_code}"))
            except Exception as e:
                print(f"[ERROR] PUT {full}: {e}")
                results.append((None, f"PUT {ep}: Error"))

            # DELETE
            try:
                r_del = requests.delete(full, headers=self.headers)
                results.append((r_del.status_code in (200, 202, 204), f"DELETE {ep}: {r_del.status_code}"))
            except Exception as e:
                print(f"[ERROR] DELETE {full}: {e}")
                results.append((None, f"DELETE {ep}: Error"))

        return results

    def test_role_bypass(self, path="/admin", fake_header_key="X-Role", fake_cookie_key="role"):
        """Test Case 4: Bypass Role-Based Access via Cookies/Headers"""
        print("\n=== Test Case 4: Role Bypass ===")
        results = []
        cookies = {fake_cookie_key: "admin"}
        headers = {**self.headers, fake_header_key: "admin"}
        try:
            r = requests.get(self.base_url + path, headers=headers, cookies=cookies, allow_redirects=False)
            results.append((r.status_code == 200, f"GET {path}: {r.status_code}"))
        except Exception as e:
            print(f"[ERROR] Role bypass {self.base_url + path}: {e}")
            results.append((None, f"GET {path}: Error"))

        return results

    def test_hidden_functions(self):
        """Test Case 5: Access Hidden Functions via JS Discovery"""
        print("\n=== Test Case 5: Hidden JS Endpoints ===")
        results = []
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
                results.append((r.status_code == 200, f"GET {ep}: {r.status_code}"))
            except Exception as e:
                print(f"[ERROR] GET {self.base_url + ep}: {e}")
                results.append((None, f"GET {ep}: Error"))

        return results

    def run_all(self):
        results = {}
        # Print the base URL only once before starting the tests
        print(f"Testing URL: {self.base_url}")
        
        # Iterate over the test methods and collect results
        for name, fn in self.tests.items():
            try:
                result = fn()  # Call the test function
                results[name] = result  # Store the test result
                # Print the vulnerability status (true for vulnerability, false for protected)
                vulnerability_status = "true" if any(v[0] for v in result) else "false"
                print(f"  {name:25s} → vulnerability:{vulnerability_status}")
            except Exception as e:
                # If an error occurs, log it and mark as None
                results[name] = None
                print(f"  {name:25s} → vulnerability:false")  # If error occurs, show false
        
        return results

if __name__ == "__main__":
    tester = BrokenAccessControlTester("http://127.0.0.1:7001")
    tester.run_all()
