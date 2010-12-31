from flask import url_for, render_template, g,\
        request, redirect, flash, session

from flaskext.principal import Identity, identity_changed, \
        identity_loaded

from route53 import app
from route53.oauth import twitter
from route53.models import db, User


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
        return redirect(request.args.get('next') or url_for('index'))


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
