from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Mock Database (ตั้งใจให้มีช่องโหว่ IDOR)
profiles = {
    1: {"name": "Alice", "email": "alice@example.com"},
    2: {"name": "Bob", "email": "bob@example.com"},
    3: {"name": "Charlie", "email": "charlie@example.com"},
}

@app.route('/')
def home():
    return '''
        <h1>🧪 Welcome to IDOR Test Site</h1>
        <p><a href="/profile?id=1">View My Profile (id=1)</a></p>
        <p>ลองเปลี่ยน id ใน URL ดู เช่น ?id=2, ?id=3 เพื่อทดสอบ IDOR</p>
    '''

@app.route('/profile')
def profile():
    user_id = request.args.get('id', type=int)
    user = profiles.get(user_id)

    if user:
        return f"""
            <h2>👤 User Profile (ID {user_id})</h2>
            <ul>
              <li><strong>Name:</strong> {user['name']}</li>
              <li><strong>Email:</strong> {user['email']}</li>
            </ul>
            <br>
            <a href="/">⬅️ Back to Home</a>
        """
    else:
        return "<h2>❌ User not found.</h2><a href='/'>⬅️ Back to Home</a>", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)