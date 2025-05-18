from flask import Flask, request, render_template_string, g, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = 'test.db'

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # === PREVENTION: enforce row factory for better safety/clarity
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

# --- Initialization route ---
@app.route('/init')
def init_db():
    """
    Initialize (or reset) the database with a default users table.
    Passwords are hashed at rest to avoid storing plaintext.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("""
      CREATE TABLE users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      );
    """)
    # === PREVENTION: hash the default password
    hashed = generate_password_hash('secret')
    cursor.execute(
        "INSERT INTO users(username, password) VALUES(?, ?);",
        ('admin', hashed)
    )
    db.commit()
    return "Database initialized. Default user: 'admin' / 'secret' (hashed)."

# --- Login template (no change) ---
LOGIN_PAGE = '''
<!doctype html>
<html>
<head><title>Secure Login</title></head>
<body>
  <h2>Login</h2>
  <form method="POST">
    Username: <input name="username"><br>
    Password: <input name="password" type="password"><br>
    <button type="submit">Login</button>
  </form>
  {% if error %}
    <p style="color:red">Error: {{ error }}</p>
  {% endif %}
</body>
</html>
'''

# --- Secure login route ---
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pwd = request.form.get('password', '')
        # === PREVENTION: use parameterized query instead of string concat
        query = "SELECT password FROM users WHERE username = ?;"
        cursor = get_db().cursor()
        cursor.execute(query, (uname,))
        row = cursor.fetchone()

        # === PREVENTION: compare hash safely and avoid revealing SQL errors
        if row and check_password_hash(row['password'], pwd):
            return render_template_string(LOGIN_PAGE, error=None, success="Logged in successfully!")
        else:
            error = 'Invalid credentials.'
    return render_template_string(LOGIN_PAGE, error=error)

# --- Secure JSON-API login ---
@app.route('/api/login-json', methods=['POST'])
def login_json():
    data = request.get_json(force=True)
    uname = data.get('username', '').strip()
    pwd = data.get('password', '')
    query = "SELECT password FROM users WHERE username = ?;"
    try:
        cursor = get_db().cursor()
        cursor.execute(query, (uname,))
        row = cursor.fetchone()
        success = bool(row and check_password_hash(row['password'], pwd))
        return jsonify({ 'success': success })
    except Exception:
        # === PREVENTION: hide internal errors from API clients
        return jsonify({ 'success': False, 'error': 'Internal server error.' }), 500

if __name__ == '__main__':
    # First visit /init to set up the database, then POST to / or /api/login-json
    app.run(debug=True)