# protected_app.py
from flask import Flask, request, jsonify, abort, redirect, url_for, session
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecret')  # PROTECTION: secret for session signing

# --- Dummy User Store ---
USERS = {
    'admin': {'password': 'secret', 'role': 'admin'},
    'user1': {'password': 'pass', 'role': 'user'}
}

# --- Authentication Helpers ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))  # PROTECTION: redirect unauthenticated users
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)  # PROTECTION: forbid non-admin access
        return f(*args, **kwargs)
    return decorated

# --- Login / Logout Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        abort(401)
    return '''
        <form method="post">
            <input name="username" placeholder="Username">
            <input name="password" type="password" placeholder="Password">
            <button>Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.clear()  # PROTECTION: clear session on logout
    return redirect(url_for('login'))

# --- Public Homepage ---
@app.route('/')
def index():
    return '<h1>Protected Test App</h1><p>Welcome, {}</p>'.format(session.get('username', 'Guest'))

# --- Admin Panel Routes ---
admin_paths = ['/admin', '/dashboard/admin', '/manage', '/admin/users', '/admin-panel']
for path in admin_paths:
    @app.route(path)
    @login_required        # PROTECTION: ensure user is logged in
    @admin_required        # PROTECTION: ensure user has admin role
    def admin_panel(path=path):
        return f"<h2>Admin Panel ({path})</h2><p>Authorized as admin.</p>"

# --- Protected API Endpoints ---
@app.route('/api/users/1', methods=['GET', 'PUT', 'DELETE'])
@login_required            # PROTECTION: authentication required
@admin_required            # PROTECTION: admin-only for modifying data
def api_user_1():
    if request.method == 'GET':
        return jsonify({"id": 1, "username": "user1", "role": "user"})
    elif request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"id": 1, **data}), 200
    elif request.method == 'DELETE':
        return '', 204

@app.route('/api/posts/10', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def api_post_10():
    if request.method == 'GET':
        return jsonify({"id": 10, "title": "Hello World", "author_id": 1})
    elif request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"id": 10, **data}), 200
    elif request.method == 'DELETE':
        return '', 204

@app.route('/admin/settings', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def admin_settings():
    if request.method == 'GET':
        return jsonify({"setting": "default"})
    elif request.method == 'PUT':
        data = request.get_json() or {}
        return jsonify({"updated": data}), 200
    elif request.method == 'DELETE':
        return '', 204

# --- Hidden Endpoints (Protected) ---
@app.route('/hidden', methods=['GET'])
@login_required            # PROTECTION: require login to discover hidden
@admin_required            # PROTECTION: admin role required
def hidden_endpoint():
    return "You've found the hidden endpoint!"

@app.route('/secret-data', methods=['GET'])
@login_required
@admin_required
def secret_data():
    return jsonify({"secret": "42"})

@app.route('/api/hidden-action', methods=['GET'])
@login_required
@admin_required
def hidden_action():
    return jsonify({"action": "executed"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)