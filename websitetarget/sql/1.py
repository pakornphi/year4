from flask import Flask, request, render_template_string, g, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'test.db'

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute(
        "CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT);")
    # Insert a default user: admin / secret
    cursor.execute(
        "INSERT INTO users(username, password) VALUES('admin','secret');")
    db.commit()
    return "Database initialized. Default user: 'admin' / 'secret'."

# --- Login template ---
LOGIN_PAGE = '''
<!doctype html>
<html>
<head><title>Vulnerable Login</title></head>
<body>
  <h2>Login</h2>
  <form method="POST">
    Username: <input name="username"><br>
    Password: <input name="password"><br>
    <button type="submit">Login</button>
  </form>
  {% if error %}
    <p style="color:red">Error: {{ error }}</p>
  {% endif %}
  {% if success %}
    <p style="color:green">{{ success }}</p>
  {% endif %}
</body>
</html>
'''

# --- Vulnerable login route ---
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    if request.method == 'POST':
        uname = request.form.get('username', '')
        pwd = request.form.get('password', '')
        # *** Vulnerable SQL concatenation ***
        query = "SELECT * FROM users WHERE username='{}' AND password='{}';".format(uname, pwd)
        try:
            cursor = get_db().cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                success = 'Logged in successfully!'
            else:
                error = 'Invalid credentials.'
        except Exception as e:
            # Show SQL errors for testing
            error = str(e)
    return render_template_string(LOGIN_PAGE, error=error, success=success)

# --- API endpoint for JSON-based testing ---
@app.route('/api/login-json', methods=['POST'])
def login_json():
    data = request.get_json(force=True)
    uname = data.get('username', '')
    pwd = data.get('password', '')
    query = "SELECT * FROM users WHERE username='{}' AND password='{}';".format(uname, pwd)
    try:
        cursor = get_db().cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify({ 'success': bool(rows), 'query': query, 'rows': len(rows) })
    except Exception as e:
        return jsonify({ 'error': str(e), 'query': query }), 500

if __name__ == '__main__':
    # To test: run this app, then visit http://localhost:5000/init first.
    app.run(debug=True , port=2000)
