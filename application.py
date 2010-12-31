from flask import Flask, url_for, render_template, g,\
        request, redirect, flash, session, request_started

from flaskext.sqlalchemy import SQLAlchemy
from flaskext.oauth import OAuth
from flaskext.principal import Identity, identity_changed, \
        identity_loaded, Principal


app = Flask(__name__)

# load configuration
app.config.from_pyfile('application.cfg')

# initialize db
db = SQLAlchemy(app)

principals = Principal(app)


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


def get_user(user_id):
    return User.query.filter_by(id=user_id).first()


# OAuth

oauth = OAuth()

twitter = oauth.remote_app('twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authenticate',
    consumer_key=app.config['CONSUMER_KEY'],
    consumer_secret=app.config['CONSUMER_SECRET']
)


@twitter.tokengetter
def get_twitter_token():
    if g.identity.name != 'anon':
        user = g.identity.user
        return (user.oauth_token, user.oauth_token_secret)
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('twitter_oauthtok', None)
    session.pop('identity.name', None)
    session.pop('identity.auth_type', None)
    return redirect(url_for('index'))


@app.route('/login')
def login():
    if g.identity.name == 'anon':
        return twitter.authorize(callback=url_for('oauth_authorized',
            next=request.args.get('next') or request.referrer or None))
    else:
        flash(u'You are already logged in with Twitter as %s'
                % g.identity.name)
        return redirect(url_for('index'))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    username = resp['screen_name']

    user = User.query.filter_by(username=username).first()

    if not user:
        user = User(username, resp['oauth_token'], resp['oauth_token_secret'])
        db.session.add(user)
        db.session.commit()

    flash('You were signed in as %s' % username)

    identity_changed.send(app, identity=Identity(username))
    return redirect(next_url)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    user = User.query.filter_by(username=identity.name).first()
    identity.user = user


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
