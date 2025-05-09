from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Query Parameter XSS
@app.route('/')
def index():
    # Reflects the 'q' parameter directly into the page without escaping
    q = request.args.get('q', '')
    html = f"""
    <h1>Search</h1>
    <form action="/" method="get">
      <input name="q" value="{q}">
      <button type="submit">Go</button>
    </form>
    <p>You searched for: {q}</p>  <!-- Vulnerable: reflected query parameter -->
    <a href="/dom?q={q}">Test DOM XSS</a>
    """
    return render_template_string(html)

# 2. Form Input XSS
@app.route('/form', methods=['GET', 'POST'])
def form_input():
    if request.method == 'POST':
        name = request.form.get('name', '')
        # Reflects form input directly
        return f"<h1>Hello, {name}!</h1>"  # Vulnerable: reflected form input
    return '''
    <h1>Enter Your Name</h1>
    <form method="post">
      <input name="name">
      <button type="submit">Submit</button>
    </form>
    '''

# 3. Header XSS
@app.route('/header')
def header_xss():
    ua = request.headers.get('User-Agent', '')
    # Reflects User-Agent header
    return f"<p>Your user agent is: {ua}</p>"  # Vulnerable: header reflection

# 4. Comment Field XSS
@app.route('/comment', methods=['GET', 'POST'])
def comment_xss():
    if request.method == 'POST':
        comment = request.form.get('comment', '')
        # Reflects comment field
        return f"<h2>Your Comment</h2><div>{comment}</div>"  # Vulnerable: comment input
    return '''
    <h1>Leave a Comment</h1>
    <form method="post">
      <textarea name="comment"></textarea>
      <button type="submit">Post</button>
    </form>
    '''

# 5. Profile Field XSS
@app.route('/profile', methods=['GET', 'POST'])
def profile_xss():
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        # Reflects profile bio
        return f"<h1>Profile</h1><p>{bio}</p>"  # Vulnerable: profile bio reflection
    return '''
    <h1>Edit Profile</h1>
    <form method="post">
      <input name="bio" placeholder="Your bio">
      <button type="submit">Save</button>
    </form>
    '''

# 6. File Upload XSS
@app.route('/upload', methods=['GET', 'POST'])
def file_upload_xss():
    if request.method == 'POST':
        f = request.files.get('file')
        if f:
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            # Reads and reflects file content
            content = open(path, 'r', encoding='utf-8').read()
            return f"<h1>Uploaded File</h1><div>{content}</div>"  # Vulnerable: file content reflected
    return '''
    <h1>Upload a File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <button type="submit">Upload</button>
    </form>
    '''

# 7. DOM-based XSS
@app.route('/dom')
def dom_xss():
    # Serves HTML that reads the 'q' parameter via JavaScript and writes it into the DOM
    html = '''
    <!doctype html>
    <html>
    <head><title>DOM XSS Test</title></head>
    <body>
      <h1>DOM XSS</h1>
      <div id="output"></div>
      <script>
        const params = new URLSearchParams(window.location.search);
        const q = params.get('q') || '';
        // Vulnerable: writes user-controlled data into the DOM without sanitization
        document.getElementById('output').innerHTML = 'You said: ' + q;
      </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run in debug mode for easy testing
