# app.py
from flask import Flask, request, jsonify, make_response, send_from_directory
import os

app = Flask(__name__, static_folder='static')

# --- Public homepage with hidden JS references ---
@app.route('/')
def index():
    html = '''
    <!doctype html>
    <html lang="en">
      <head><meta charset="utf-8"><title>Test Target</title></head>
      <body>
        <h1>Welcome to the Broken Access Control Test Target</h1>
        <script src="/static/app.js"></script>
      </body>
    </html>
    '''
    return html

# --- Admin panel endpoints (broken access control) ---
admin_paths = ['/admin', '/dashboard/admin', '/manage', '/admin/users', '/admin-panel']
for p in admin_paths:
    @app.route(p, methods=['GET'])
    def admin_panel(p=p):
        # Trusts user-supplied header or cookie for role
        role_header = request.headers.get('X-Role')
        role_cookie = request.cookies.get('role')
        if role_header == 'admin' or role_cookie == 'admin':
            return f"<h2>Admin Panel ({p})</h2>\n<p>Authorized as admin.</p>"
        return make_response("<h2>Forbidden</h2><p>You are not allowed.</p>", 403)

# --- API endpoints vulnerable to PUT/DELETE escalation ---
@app.route('/api/users/1', methods=['GET', 'PUT', 'DELETE'])
def api_user_1():
    if request.method == 'GET':
        return jsonify({"id": 1, "username": "user1", "role": "user"})
    if request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"id": 1, **data}), 200
    if request.method == 'DELETE':
        return '', 204

@app.route('/api/posts/10', methods=['GET', 'PUT', 'DELETE'])
def api_post_10():
    if request.method == 'GET':
        return jsonify({"id": 10, "title": "Hello World", "author_id": 1})
    if request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"id": 10, **data}), 200
    if request.method == 'DELETE':
        return '', 204

@app.route('/admin/settings', methods=['GET', 'PUT', 'DELETE'])
def admin_settings():
    if request.method == 'GET':
        return jsonify({"setting": "default"})
    if request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"updated": data}), 200
    if request.method == 'DELETE':
        return '', 204

# --- Hidden endpoints to be discovered via JS ---
@app.route('/hidden', methods=['GET'])
def hidden_endpoint():
    return "You've found the hidden endpoint!"

@app.route('/secret-data', methods=['GET'])
def secret_data():
    return jsonify({"secret": "42"})

# --- Static JS file exposing hidden URLs in strings ---
# static/app.js
# --------------------------------
# // Application JavaScript
# console.log('App loaded');
# // Available hidden routes:
# var endpoints = ['/hidden', '/secret-data', '/api/hidden-action'];
# function ping(endpoint) {
#   fetch(endpoint).then(res => console.log(endpoint, res.status));
# }
# endpoints.forEach(e => ping(e));

# Additional hidden action endpoint
@app.route('/api/hidden-action', methods=['GET'])
def hidden_action():
    return jsonify({"action": "executed"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)