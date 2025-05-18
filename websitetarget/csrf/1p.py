from flask import (
    Flask, request, abort, session,
    render_template_string, redirect, url_for
)
import uuid
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_real_secret'

# === CONFIG: how long a token stays valid
CSRF_EXPIRATION = timedelta(minutes=5)

def generate_csrf_token():
    """
    === PREVENTION:
    - Generate a fresh, unpredictable token.
    - Store it + timestamp in session.
    """
    token = uuid.uuid4().hex
    session['csrf_token'] = token
    session['csrf_token_time'] = datetime.utcnow().isoformat()
    return token

def validate_csrf(token):
    """
    === PREVENTION:
    - Verify token matches session.
    - Verify token not expired.
    """
    saved = session.get('csrf_token')
    saved_time = session.get('csrf_token_time')
    if not saved or not saved_time or token != saved:
        return False
    created = datetime.fromisoformat(saved_time)
    if datetime.utcnow() - created > CSRF_EXPIRATION:
        return False
    return True

def csrf_protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            # === PREVENTION: double-submit check
            form_token = request.form.get('csrf_token')
            cookie_token = request.cookies.get('csrf_token')
            if not form_token or not cookie_token:
                abort(403)
            if form_token != cookie_token:
                abort(403)
            # === PREVENTION: expiration & correctness
            if not validate_csrf(form_token):
                abort(403)
        return f(*args, **kwargs)
    return wrapper

@app.after_request
def inject_csrf_cookie(response):
    """
    === PREVENTION:
    - Send the CSRF token as a non-HttpOnly cookie
      so JavaScript can read it if needed for XHR.
    """
    token = session.get('csrf_token')
    if token:
        response.set_cookie(
            'csrf_token',
            token,
            secure=False,      # set True in prod (HTTPS)
            httponly=False     # must be False for double-submit
        )
    return response

# ---- Secure Root Form ----
@app.route('/', methods=['GET', 'POST'])
@csrf_protect
def index():
    if request.method == 'GET':
        # === PREVENTION: rotate token on each GET
        token = generate_csrf_token()
        return render_template_string('''
        <h2>Secure Root Form</h2>
        <form method="post">
          <input type="hidden" name="csrf_token" value="{{token}}">
          <input type="text" name="data" placeholder="some data">
          <button>Submit</button>
        </form>''', token=token)
    else:
        return '✓ root submission accepted securely'

# ---- Secure Missing-CSRF Fixed ----
@app.route('/missing_csrf', methods=['GET', 'POST'])
@csrf_protect
def missing_csrf():
    if request.method == 'GET':
        token = generate_csrf_token()
        return render_template_string('''
        <h2>Now Protected: Form with CSRF field</h2>
        <form method="post">
          <input type="hidden" name="csrf_token" value="{{token}}">
          <input name="data">
          <button>Go</button>
        </form>''', token=token)
    else:
        return '✓ submitted securely (CSRF enforced)'

# ---- Secure Static-CSRF Fixed (now dynamic) ----
@app.route('/static_csrf', methods=['GET', 'POST'])
@csrf_protect
def static_csrf():
    if request.method == 'GET':
        # === PREVENTION: dynamic token instead of static
        token = generate_csrf_token()
        return render_template_string('''
        <h2>Fixed: Dynamic CSRF Token</h2>
        <form method="post">
          <input type="hidden" name="csrf_token" value="{{token}}">
          <input name="data">
          <button>Send</button>
        </form>''', token=token)
    else:
        return '✓ static_csrf accepted securely'

# ---- Secure Malformed-CSRF Fixed ----
@app.route('/malformed_csrf', methods=['GET', 'POST'])
@csrf_protect
def malformed_csrf():
    if request.method == 'GET':
        token = generate_csrf_token()
        return render_template_string('''
        <h2>Fixed: Reject Malformed Tokens</h2>
        <form method="post">
          <input type="hidden" name="csrf_token" value="{{token}}">
          <input name="data">
          <button>Okay</button>
        </form>''', token=token)
    else:
        # token validation already enforced by decorator
        return '✓ malformed_csrf accepted securely'

# ---- Secure Login: Session Fixation Protection ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # === PREVENTION: clear session to rotate on GET
        session.clear()
        token = generate_csrf_token()
        return render_template_string('''
        <h2>Login (Session Rotated)</h2>
        <form method="post">
          <input type="hidden" name="csrf_token" value="{{token}}">
          <input name="username" placeholder="user">
          <input type="password" name="password">
          <button>Log in</button>
        </form>''', token=token)
    else:
        # === PREVENTION: ensure CSRF & rotate session after login
        if not validate_csrf(request.form.get('csrf_token')):
            abort(403)
        session.clear()
        generate_csrf_token()
        return '✓ login submitted securely'

if __name__ == '__main__':
    app.run(debug=True)
