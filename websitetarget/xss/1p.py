from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Query Parameter XSS Protection
@app.route('/')
def index():
    q = request.args.get('q', '')
    html = """
    <h1>Search</h1>
    <form action="/" method="get">
      <input name="q" value="{{ q|e }}">
      <button type="submit">Go</button>
    </form>
    <p>You searched for: {{ q|e }}</p>  <!-- Protected: Jinja2 autoescaping -->
    <a href="/dom?q={{ q|urlencode }}">Test DOM XSS</a>  <!-- Protected: URL encoding -->
    """
    return render_template_string(html, q=q)

# 2. Form Input XSS Protection
@app.route('/form', methods=['GET', 'POST'])
def form_input():
    if request.method == 'POST':
        name = request.form.get('name', '')
        # Protected: using Jinja2 autoescaping
        return render_template_string("<h1>Hello, {{ name|e }}!</h1>", name=name)
    return '''
    <h1>Enter Your Name</h1>
    <form method="post">
      <input name="name">
      <button type="submit">Submit</button>
    </form>
    '''

# 3. Header XSS Protection
@app.route('/header')
def header_xss():
    ua = request.headers.get('User-Agent', '')
    # Protected: escape header via Jinja2
    return render_template_string("<p>Your user agent is: {{ ua|e }}</p>", ua=ua)

# 4. Comment Field XSS Protection
@app.route('/comment', methods=['GET', 'POST'])
def comment_xss():
    if request.method == 'POST':
        comment = request.form.get('comment', '')
        # Protected: escape comment input
        return render_template_string("<h2>Your Comment</h2><div>{{ comment|e }}</div>", comment=comment)
    return '''
    <h1>Leave a Comment</h1>
    <form method="post">
      <textarea name="comment"></textarea>
      <button type="submit">Post</button>
    </form>
    '''

# 5. Profile Field XSS Protection
@app.route('/profile', methods=['GET', 'POST'])
def profile_xss():
    if request.method == 'POST':
        bio = request.form.get('bio', '')
        # Protected: escape profile bio
        return render_template_string("<h1>Profile</h1><p>{{ bio|e }}</p>", bio=bio)
    return '''
    <h1>Edit Profile</h1>
    <form method="post">
      <input name="bio" placeholder="Your bio">
      <button type="submit">Save</button>
    </form>
    '''

# 6. File Upload XSS Protection
@app.route('/upload', methods=['GET', 'POST'])
def file_upload_xss():
    if request.method == 'POST':
        f = request.files.get('file')
        if f:
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            # Protected: escape file content and wrap in <pre>
            return render_template_string("<h1>Uploaded File</h1><pre>{{ content|e }}</pre>", content=content)
    return '''
    <h1>Upload a File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <button type="submit">Upload</button>
    </form>
    '''

# 7. DOM-based XSS Protection
@app.route('/dom')
def dom_xss():
    # Serves HTML using textContent instead of innerHTML
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
        // Protected: use textContent to prevent HTML injection
        document.getElementById('output').textContent = 'You said: ' + q;
      </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(debug=True, port=5000)
