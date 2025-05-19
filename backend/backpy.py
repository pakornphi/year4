from flask import Flask, request, jsonify
from flask_cors import CORS
from csrf2 import CSRFTester  # Assuming CSRFTester is in csrf_tester.py
from xss import XSSTester
from sql import SQLInjectionTester  # Import SQLInjectionTester from sql.py
import logging
from BAC import BrokenAccessControlTester  # Import the BrokenAccessControlTester from BAC.py
from Idor import IDORSummarizedTester  # ← เพิ่มส่วน import นี้
import os
import importlib.util

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication


def load_payloads_from_py(path: str = 'payloads.py') -> list[str]:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")
    spec = importlib.util.spec_from_file_location("payloads_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, 'PAYLOADS'):
        raise AttributeError(f"No PAYLOADS in {path}")
    return getattr(mod, 'PAYLOADS')


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

# @app.before_request
# def limit_to_localtunnel():
#     origin = request.headers.get("Origin") or ""
#     host = request.host or ""

#     if "loca.lt" not in origin and "loca.lt" not in host:
#         return jsonify({"error": "❌ Access allowed only via loca.lt domain"}), 403
    
# XSS Tester class is used in this route
@app.route('/api/test-xss', methods=['POST'])
def test_xss():
    data = request.get_json(force=True)
    target_url = data.get('url')
    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # 1) load payloads
        payloads = load_payloads_from_py('payloads.py')

        # 2) run the tester (now returns a dict)
        tester = XSSTester(
            base_url=target_url,
            payloads=payloads,
            timeout=3,
            cooldown=0.5,
            workers=10
        )
        raw_results = tester.run_all()   # dict: { test_name: [hits…], … }

        # 3) build the lines array
        labels = {
            'test_query_parameter_xss': 'Query Parameter XSS',
            'test_form_input_xss':      'Form Input XSS',
            'test_header_xss':          'Header XSS',
            'test_comment_xss':         'Comment Field XSS',
            'test_profile_field_xss':   'Profile Field XSS',
            'test_file_upload_xss':     'File Upload XSS',
        }

        lines = []
        for test_name, hits in raw_results.items():
            label = labels.get(test_name, test_name).ljust(30)
            # use None if you want “vulnerability:None” when no verdict,
            # or boolean if you prefer True/False
            vuln = None if hits is None else bool(hits)
            lines.append(f"{label} → vulnerability:{vuln}")

        return jsonify({
            "tested_url": target_url,
            "results": lines
        }), 200

    except Exception as e:
        return jsonify({'error': f'XSS test failed: {e}'}), 500


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

        # 🔧 เปลี่ยน format ของ report ให้เป็นแบบที่คุณต้องการ
        summary_lines = []
        for name, details in raw_results.items():
            count = sum(1 for ok, _ in details if ok)
            status = "True" if count > 0 else "False"
            summary_lines.append(f"{name:35s}vulnerability:{status}")

        return jsonify({
            "tested_url": target_url,
            "report": summary_lines
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
