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
    data = request.get_json()  # Get the JSON data from the POST request
    base_url = data.get('url')  # The URL to test

    if not base_url:
        return jsonify({"error": "URL is required"}), 400

    # Initialize the CSRFTester with the provided base_url
    tester = CSRFTester(base_url=base_url)

    # Run the CSRF tests
    results = tester.run_all()

    # Initialize result_data with the tested URL
    result_data = {
        "tested_url": base_url  # Include the URL in the response data
    }

    # Add results for each test
    for name, (vuln, info) in results.items():
        result_data[name] = {
            "vulnerability": vuln,
            "info": info
        }

    # Return the test results as a JSON response
    return jsonify(result_data)


# XSS Tester class is used in this route
@app.route('/api/test-xss', methods=['POST'])
def test_xss():
    data = request.get_json()
    target_url = data.get('url')
    print("✅ /api/test-xss called")

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        tester = XSSTester(
            base_url=target_url,
            payload_file='payload.txt',
            timeout=3,
            cooldown=0.5,
            workers=10
        )

        raw_results = tester.run_all(max_workers=tester.workers)

        for name, payloads in raw_results.items():
            if name == 'vulnerability':
                print(f"vulnerability: {'YES' if payloads else 'NO'}")
            else:
                print(f"[INFO] {name}: {len(payloads)} payloads triggered vulnerability")
                print(f"{name}: {len(payloads)} vulnerable payload(s)")

        results = {
            name: {'count': len(payloads), 'payloads': payloads}
            for name, payloads in raw_results.items() if name != 'vulnerability'
        }
        results['vulnerability'] = raw_results.get('vulnerability', False)

        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({'error': f'XSS test failed: {str(e)}'}), 500

# SQL Injection Tester class is used in this route
@app.route('/api/test-sql', methods=['POST'])
def test_sql_injection():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        tester = SQLInjectionTester(
            base_url=target_url,
            endpoints=['/', '/login'],  # Adjust according to your target app's endpoints
            timeout=5.0
        )
        
        # Run the SQL Injection test
        vuln_found, payload = tester.test_sql_injection()
        
        # Return results based on whether a vulnerability was found
        if vuln_found:
            return jsonify({
                'vulnerable': True,
                'payload': payload
            }), 200
        else:
            return jsonify({
                'vulnerable': False,
                'message': 'No vulnerabilities detected'
            }), 200

    except Exception as e:
        return jsonify({'error': f'SQL Injection test failed: {str(e)}'}), 500

# New route for Broken Access Control testing
@app.route('/api/test-broken-access-control', methods=['POST'])
def test_broken_access_control():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Initialize the BrokenAccessControlTester with the provided base_url
        tester = BrokenAccessControlTester(base_url=target_url)

        # Run all tests
        results = tester.run_all()

        # Return the results as a JSON response
        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({'error': f'Broken Access Control test failed: {str(e)}'}), 500
    


@app.route('/api/test-idor', methods=['POST'])
def test_idor():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        tester = IDORSummarizedTester(url=target_url)
        results = tester.test()
        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({'error': f'IDOR test failed: {str(e)}'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
