from flask import url_for, g,\
        request, redirect, flash

from flaskext.oauth import OAuth

from route53 import app


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


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    from route53.models import db, User
    from flaskext.principal import Identity, identity_changed
    next_url = request.args.get('next') or url_for('auth.index')
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

    from route53 import app
    identity_changed.send(app, identity=Identity(username))
    return redirect(next_url)
