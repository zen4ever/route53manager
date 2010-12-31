from flask import g
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
