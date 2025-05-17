# bac_improved.py
import requests
import re
from urllib.parse import urljoin
import sys

class BrokenAccessControlTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "AccessControlTester/1.0"}
        self.json_headers = {**self.headers, "Content-Type": "application/json"}
        # Map descriptive test names to methods
        self.tests = {
            'Admin Panel Access': self.test_admin_panel,
            'HTTP Methods Privilege Escalation': self.test_http_methods,
            'Role Bypass Protection': self.test_role_bypass,
            'Hidden JS Endpoint Access': self.test_hidden_functions
        }

    def _print_header(self):
        print(f"Testing URL: {self.base_url}\n")

    def _report(self, name, results):
        # Determine if any result is True (vulnerable)
        vuln = any(r[0] for r in results if r[0] is not None)
        status = 'True' if vuln else 'False'
        print(f"  {name:30s} → vulnerability:{status}")

    def test_admin_panel(self, paths=None):
        if paths is None:
            paths = ["/admin", "/dashboard/admin", "/manage", "/admin/users", "/admin-panel"]
        results = []
        for p in paths:
            try:
                r = requests.get(self.base_url + p, headers=self.headers, allow_redirects=False)
                results.append((r.status_code == 200, f"GET {p}: {r.status_code}"))
            except Exception:
                results.append((None, f"GET {p}: Error"))
        return results

    def test_http_methods(self, endpoints=None, payload=None):
        if endpoints is None:
            endpoints = ["/api/users/1", "/api/posts/10", "/admin/settings"]
        if payload is None:
            payload = {"role": "admin", "username": "hacker"}
        results = []
        for ep in endpoints:
            full = self.base_url + ep
            try:
                r_put = requests.put(full, json=payload, headers=self.json_headers)
                results.append((r_put.status_code in (200, 201, 204), f"PUT {ep}: {r_put.status_code}"))
            except Exception:
                results.append((None, f"PUT {ep}: Error"))
            try:
                r_del = requests.delete(full, headers=self.headers)
                results.append((r_del.status_code in (200, 202, 204), f"DELETE {ep}: {r_del.status_code}"))
            except Exception:
                results.append((None, f"DELETE {ep}: Error"))
        return results

    def test_role_bypass(self, path="/admin", hdr_key="X-Role", cookie_key="role"):
        results = []
        cookies = {cookie_key: "admin"}
        headers = {**self.headers, hdr_key: "admin"}
        try:
            r = requests.get(self.base_url + path, headers=headers, cookies=cookies, allow_redirects=False)
            results.append((r.status_code == 200, f"GET {path}: {r.status_code}"))
        except Exception:
            results.append((None, f"GET {path}: Error"))
        return results

    def test_hidden_functions(self):
        results = []
        try:
            home = requests.get(self.base_url, headers=self.headers).text
        except Exception:
            return [(None, "Fetch main page error")]
        js_files = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', home)
        js_urls = [urljoin(self.base_url, src) for src in js_files]
        endpoints = set()
        for js in js_urls:
            try:
                content = requests.get(js, headers=self.headers).text
                found = re.findall(r'["\'](\/[A-Za-z0-9_\-/]+?)["\']', content)
                endpoints.update(found)
            except Exception:
                continue
        for ep in sorted(endpoints):
            try:
                r = requests.get(self.base_url + ep, headers=self.headers, allow_redirects=False)
                results.append((r.status_code == 200, f"GET {ep}: {r.status_code}"))
            except Exception:
                results.append((None, f"GET {ep}: Error"))
        return results

    def run_all(self):
        self._print_header()
        results = {}
        for name, fn in self.tests.items():
            res = fn()
            self._report(name, res)
            results[name] = res
        return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python bac_improved.py <target_url>")
    else:
        tester = BrokenAccessControlTester(sys.argv[1])
<<<<<<< HEAD
        tester.run_all()
=======
        tester.run_all()
>>>>>>> 8120034 (bac xss)
