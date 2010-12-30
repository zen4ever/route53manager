from flask import Flask, url_for, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

try:
    from local_settings import SECRET_KEY
    app.secret_key = SECRET_KEY
except ImportError:
    pass

if __name__ == '__main__':
    app.run(debug=True)
