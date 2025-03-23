from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from csrf import CSRFTester  # Import CSRF Tester class

app = Flask(__name__)

# Enable CORS for all routes (allows React to communicate with Flask)
CORS(app)

@app.route('/api/test-csrf', methods=['POST'])
def test_csrf():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    # Create an instance of CSRFTester with the target URL
    tester = CSRFTester(target_url)

    # Perform CSRF tests
    test_results = tester.perform_test()

    return jsonify({'results': test_results}), 200

if __name__ == '__main__':
    app.run(debug=True)
