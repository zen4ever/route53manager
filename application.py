from flask import Flask, url_for, render_template

from flaskext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('application.cfg')
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html') 

if __name__ == '__main__':
    app.run()
