from flask import Flask, request, abort
import uuid

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_real_secret'

# ---- Static tokens ----
# Root token for expiration / double-submit-cookie tests
root_token = str(uuid.uuid4())
# Static token for reuse / static-rotation tests
static_csrf_token = str(uuid.uuid4())

# ---- ROOT: expiration + missing double-submit cookie ----
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return f'''
        <html><body>
          <h2>Root form (no expiry, no double-submit cookie)</h2>
          <form action="/" method="post">
            <input type="hidden" name="csrf_token" value="{root_token}"/>
            <input type="text" name="data" placeholder="some data"/>
            <input type="submit" value="Submit"/>
          </form>
        </body></html>
        '''
    else:
        token = request.form.get('csrf_token')
        # enforce presence and correctness, but never expire
        if token != root_token:
            abort(403)
        return '✓ root submission accepted'

# ---- 1) Missing CSRF Token ----
@app.route('/missing_csrf', methods=['GET', 'POST'])
def missing_csrf():
    if request.method == 'GET':
        return '''
        <html><body>
          <h2>Form with NO CSRF field</h2>
          <form action="/missing_csrf" method="post">
            <input type="text" name="data"/>
            <input type="submit" value="Go"/>
          </form>
        </body></html>
        '''
    else:
        return '✓ submitted (no CSRF)'

# ---- 2 & 4) Static CSRF & Reuse Allowed ----
@app.route('/static_csrf', methods=['GET', 'POST'])
def static_csrf():
    if request.method == 'GET':
        return f'''
        <html><body>
          <h2>Static CSRF token (never rotates, reuse allowed)</h2>
          <form action="/static_csrf" method="post">
            <input type="hidden" name="csrf_token" value="{static_csrf_token}"/>
            <input type="text" name="data"/>
            <input type="submit" value="Send"/>
          </form>
        </body></html>
        '''
    else:
        token = request.form.get('csrf_token')
        if token != static_csrf_token:
            abort(403)
        return '✓ static_csrf accepted'

# ---- 3) Malformed Token Accepted ----
@app.route('/malformed_csrf', methods=['GET', 'POST'])
def malformed_csrf():
    if request.method == 'GET':
        # generate a token so the tester knows its length
        token = str(uuid.uuid4())
        return f'''
        <html><body>
          <h2>Accepts ANY token of the same length</h2>
          <form action="/malformed_csrf" method="post">
            <input type="hidden" name="csrf_token" value="{token}"/>
            <input type="text" name="data"/>
            <input type="submit" value="Okay"/>
          </form>
        </body></html>
        '''
    else:
        # blindly accept whatever is submitted
        return '✓ malformed_csrf accepted'

# ---- 7) Session Fixation Protection (vulnerable) ----
@app.route('/login', methods=['GET'])
def login():
    # does NOT rotate the session cookie on GET
    return '''
    <html><body>
      <h2>Login page (no session rotation)</h2>
      <form action="/login" method="post">
        <input type="text" name="username"/>
        <input type="password" name="password"/>
        <input type="submit" value="Log in"/>
      </form>
    </body></html>
    '''

@app.route('/login', methods=['POST'])
def login_post():
    return '✓ login submitted'

if __name__ == '__main__':
    app.run(debug=True, port=1000)