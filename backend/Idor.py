import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

class IDORTester:
    def __init__(self, target_url, id_param="id", start_id=1, end_id=5):
        """
        :param target_url: URL ที่จะทดสอบ (ต้องมี parameter เช่น ?id=1)
        :param id_param: ชื่อ parameter ที่ใช้เป็นตัวระบุ เช่น id, user_id
        :param start_id: เริ่มทดสอบตั้งแต่ id เท่าไหร่
        :param end_id: ทดสอบถึง id เท่าไหร่
        """
        self.target_url = target_url
        self.id_param = id_param
        self.start_id = start_id
        self.end_id = end_id
        self.session = requests.Session()
        self.results = []

    def modify_url(self, original_url, new_id):
        """แก้ไข URL เปลี่ยน id เป็น new_id"""
        parsed_url = urlparse(original_url)
        query_params = parse_qs(parsed_url.query)
        query_params[self.id_param] = [str(new_id)]
        new_query = urlencode(query_params, doseq=True)
        new_url = parsed_url._replace(query=new_query).geturl()
        return new_url

    def test_idor(self):
        """ทำการทดสอบ IDOR โดยการเปลี่ยน id แล้วดูว่าข้อมูลเปลี่ยนหรือไม่"""
        self.results.append(f"Starting IDOR test for: {self.target_url}")

        try:
            base_response = self.session.get(self.target_url)
            base_content = base_response.text.strip()
        except Exception as e:
            self.results.append(f"Error fetching base URL: {e}")
            return self.results

        for test_id in range(self.start_id, self.end_id + 1):
            test_url = self.modify_url(self.target_url, test_id)

            try:
                response = self.session.get(test_url)
                content = response.text.strip()

                if content != base_content:
                    self.results.append(f"⚠️ Potential IDOR detected at ID={test_id}: Different content returned.")
                else:
                    self.results.append(f"✅ No IDOR detected at ID={test_id} (same content).")

            except Exception as e:
                self.results.append(f"Error fetching {test_url}: {e}")

        return self.results