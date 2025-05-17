from flask import Flask, request, render_template_string

app = Flask(__name__)

# Simple in-memory "database" for users (for demonstration purposes)
users = []

@app.route('/')
def index():
    return render_template_string("""
    <html>
    <body>
        <h1>Sign Up</h1>
        <form method="POST" action="/send">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <br>
            <button type="send">send</button>
        </form>
    </body>
    </html>
    """)

@app.route('/send', methods=['POST'])
def submit():
    # Normally, there should be a CSRF token check here, but we're leaving it out for demonstration.
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simulate storing user data
    users.append({'username': username, 'password': password})
    return f"User {username} registered successfully!"

if __name__ == '__main__':
    app.run(debug=True)
