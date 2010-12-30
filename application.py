from flask import Flask, url_for, render_template, \
        request, redirect, flash, session

from flaskext.sqlalchemy import SQLAlchemy
from flaskext.oauth import OAuth


app = Flask(__name__)
app.config.from_pyfile('application.cfg')
db = SQLAlchemy(app)

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
        return session.get('twitter_token')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
            resp['oauth_token'],
            resp['oauth_token_secret']
        )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    return redirect(next_url)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
