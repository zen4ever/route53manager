from route53 import app
from flaskext.sqlalchemy import SQLAlchemy

# initialize db
db = SQLAlchemy(app)

# Models

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    oauth_token = db.Column(db.String(255))
    oauth_token_secret = db.Column(db.String(255))

    def __init__(self, username, oauth_token, oauth_token_secret):
        self.username = username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    def is_authenticated(self):
        return True

    def __repr__(self):
        return '<User %r>' % self.username
