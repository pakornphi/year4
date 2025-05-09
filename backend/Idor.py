# idor.py
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
        self.results = []

    def modify_url(self, param, value):
        parsed = urlparse(self.url)
        query = parse_qs(parsed.query)
        query[param] = [str(value)]
        new_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def test(self):
        try:
            base_resp = self.session.get(self.url, timeout=self.timeout)
            base_text = base_resp.text.strip()
            base_status = base_resp.status_code
        except Exception as e:
            return [f"❌ Failed to fetch base URL: {e}"]

        for param in COMMON_PARAMS:
            changed = False
            for val in range(self.start, self.end + 1):
                test_url = self.modify_url(param, val)
                try:
                    resp = self.session.get(test_url, timeout=self.timeout)
                    if resp.status_code != base_status or resp.text.strip() != base_text:
                        changed = True
                        break
                except Exception as e:
                    changed = f"❌ Error: {e}"
                    break

            if isinstance(changed, str):
                self.results.append({param: changed})
            elif changed:
                self.results.append({param: "⚠️ Potential IDOR (changed)"})
            else:
                self.results.append({param: "✅ No IDOR (same content)"})

        return self.results
