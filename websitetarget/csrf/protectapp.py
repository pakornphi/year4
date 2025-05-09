#protect token dubmit no token reuse token 
from flask import Flask, request, render_template_string, abort, session, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect, generate_csrf

app = Flask(__name__)

# Secret key for CSRF protection
app.config['SECRET_KEY'] = 'a_secure_and_random_secret_key'

# Enable CSRF protection globally for all forms
csrf = CSRFProtect(app)

# Simple in-memory "database" for users (for demonstration purposes)
users = []

# Define the form with CSRF protection
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/')
def index():
    form = SignupForm()

    # Force regeneration of CSRF token for every request
    csrf_token = generate_csrf()

    # Render the template string
    html = render_template_string("""
    <html>
    <body>
        <h1>Sign Up</h1>
        <form method="POST" action="/send">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">  <!-- This renders the CSRF token -->
            <label for="username">Username:</label>
            {{ form.username() }}
            <br>
            <label for="password">Password:</label>
            {{ form.password() }}
            <br>
            <button type="submit">Send</button>
        </form>
    </body>
    </html>
    """, form=form, csrf_token=csrf_token)

    # Create a response object and set cache control headers
    response = make_response(html)
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.expires = 0
    return response

@app.route('/send', methods=['POST'])
def submit():
    form = SignupForm()

    # Manually validate CSRF token here to catch any issues with token validation
    csrf_token_from_request = request.form.get('csrf_token')
    csrf_token_from_session = session.get('_csrf_token')

    if csrf_token_from_request != csrf_token_from_session:
        abort(400, description="CSRF token missing or invalid.")

    # This will automatically validate the CSRF token via Flask-WTF
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Simulate storing user data
        users.append({'username': username, 'password': password})

        # After the form is successfully submitted, invalidate the CSRF token
        # by manually removing it from the session
        session.pop('_csrf_token', None)

        return f"User {username} registered successfully!"
    else:
        # This ensures invalid requests are rejected with a 400 Bad Request
        abort(400, description="CSRF token missing or invalid.")

if __name__ == '__main__':
    app.run(debug=True)
