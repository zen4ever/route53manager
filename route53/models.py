from route53 import app

from flaskext.sqlalchemy import SQLAlchemy
from flaskext.principal import identity_loaded

# initialize db
db = SQLAlchemy(app)

# Models

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    oauth_token = db.Column(db.String(255))
    oauth_token_secret = db.Column(db.String(255))
    credentials = db.relation("AWSCredential", backref="user")

    def __init__(self, username, oauth_token, oauth_token_secret):
        self.username = username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

    def first_credentials(self):
        return self.credentials[0]

    def __repr__(self):
        return "<User %r>" % self.username


class AWSCredential(db.Model):
    __tablename__ = "aws_credentials"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255))
    access_key_id = db.Column(db.String(255))
    secret_access_key = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, nickname, access_key_id, secret_access_key, user_id):
        self.nickname = nickname
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.user_id = user_id

    def __repr__(self):
        return "<AWSCredentials %r>" % self.nickname


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    user = User.query.filter_by(username=identity.name).first()
    identity.user = user
