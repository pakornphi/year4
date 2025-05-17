from flask import Flask, request, jsonify
from flask_cors import CORS
from csrf2 import CSRFTester  # Assuming CSRFTester is in csrf_tester.py
from xss import XSSTester
from sql import SQLInjectionTester  # Import SQLInjectionTester from sql.py
import logging
from BAC import BrokenAccessControlTester  # Import the BrokenAccessControlTester from BAC.py
from Idor import IDORSummarizedTester  # ← เพิ่มส่วน import นี้

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# CSRF Tester class is used in this route
@app.route('/api/test-csrf', methods=['POST'])
def test_csrf():
    data = request.get_json()
    base_url = data.get('url')

    if not base_url:
        return jsonify({"error": "URL is required"}), 400

    print(f"✅ /api/test-csrf received for: {base_url}")
    tester = CSRFTester(base_url=base_url)
    raw_results = tester.run_all()

    # ✅ จัดรูปแบบเป็นข้อความเพื่อใช้แสดงผลและเก็บใน localStorage
    formatted = []
    for name, (vuln, info) in raw_results.items():
        line = f"{name:30s} → vulnerability:{vuln}"
        if info:
            line += f"   info={info}"
        formatted.append(line)

    return jsonify({
        "tested_url": base_url,
        "results": formatted   # ✅ list[string]
    }), 200


# XSS Tester class is used in this route
@app.route('/api/test-xss', methods=['POST'])
def test_xss():
    data = request.get_json()
    target_url = data.get('url')
    print(f"✅ /api/test-xss called for: {target_url}")

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # ✅ ระบุ payload.txt ไว้ตรงนี้โดยตรง
        tester = XSSTester(
            base_url=target_url,
            payload_file='payload.txt',   # ← อย่าลืมให้ไฟล์นี้อยู่ใน backend folder
            timeout=3,
            cooldown=0.5,
            workers=10
        )

        raw_results = tester.run_all()
        print(f"📦 Raw Results: {raw_results}")

        # ✅ แปลง raw_results เป็นโครงสร้าง JSON ที่ dashboard ใช้ได้
        results = {
            name: {
                'count': count,
                'payloads': []  # หรือใส่ actual payload ถ้ามี logic
            }
            for name, count in raw_results.items()
            if name != 'vulnerability'
        }

        results['vulnerability'] = raw_results.get('vulnerability', False)

        return jsonify({'results': results}), 200

    except Exception as e:
        print(f"❌ XSS test failed: {e}")
        return jsonify({'error': f'XSS test failed: {str(e)}'}), 500



# SQL Injection Tester class is used in this route

@app.route('/api/test-sql', methods=['POST'])
def test_sql_injection():
    print("✅ /api/test-sql called")
    try:
        data = request.get_json(force=True)
        target_url = data.get('url')
        print("➡️ Target URL:", target_url)

        if not target_url:
            return jsonify({'error': 'URL is required'}), 400

        tester = SQLInjectionTester(
            base_url=target_url,
            timeout=5.0
        )

        results = tester.run_all()  # ✅ ใช้ run_all ไม่ใช่ run_tests

        # format เป็น string[] เพื่อแสดงผล
        formatted = []
        for name, is_vuln in results.items():
            line = f"{name:35s} → vulnerability:{is_vuln[0]}"
            formatted.append(line)

        return jsonify({
            'tested_url': target_url,
            'results': formatted
        }), 200

    except Exception as e:
        print("❌ SQL test failed:", e)
        return jsonify({'error': f'SQL Injection test failed: {e}'}), 500



# New route for Broken Access Control testing
@app.route('/api/test-broken-access-control', methods=['POST'])
def test_broken_access_control():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        tester = BrokenAccessControlTester(base_url=target_url)
        raw_results = tester.run_all()

        formatted = []
        for name, details in raw_results.items():
            if isinstance(details, list):
                count = sum(1 for d in details if d[0] is True)
                status = "True" if count > 0 else "False"
                formatted.append(f"{name:30s} → vulnerability:{status}")
                for d in details:
                    formatted.append(f"    {d[1]}")

        return jsonify({
            "tested_url": target_url,
            "results": formatted  # ✅ ชัดเจนเลย
        }), 200

    except Exception as e:
        return jsonify({'error': f'BAC test failed: {str(e)}'}), 500

@app.route('/api/test-idor', methods=['POST'])
def test_idor():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        tester = IDORSummarizedTester(url=target_url)
        raw_results = tester.run_all()  # {'id': True, 'user_id': True, ...}

        messages = []
        for param, is_vuln in raw_results.items():
            label = tester.descriptive_names.get(param, param).ljust(30)
            status = 'True' if is_vuln else 'False'
            line = f"{label} → vulnerability:{status}"
            messages.append(line)

        is_vulnerable = any(v for v in raw_results.values())

        return jsonify({
            "tested_url": target_url,
            "idor_vulnerable": is_vulnerable,
            "messages": messages
        }), 200

    except Exception as e:
        return jsonify({'error': f'IDOR test failed: {str(e)}'}), 500

    
if __name__ == '__main__':
    app.run(debug=True)
