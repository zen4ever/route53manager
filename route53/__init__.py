import urllib

from flask import Flask

from route53.views.zones import zones
from route53.views.main import main
from route53.views.records import records
from route53.views.slicehost import slicehost

from auth import FlaskRealmDigestDB, AuthMiddleware

app = Flask(__name__)
app.register_module(main)
app.register_module(zones, url_prefix='/zones')
app.register_module(records, url_prefix='/records')
app.register_module(slicehost, url_prefix='/slicehost')

# load configuration
app.config.from_pyfile('application.cfg')


@app.template_filter('shortid')
def shortid(s):
    return s.replace('/hostedzone/', '')


@app.template_filter('urlencode')
def urlencode(s):
    return urllib.quote(s, '/')

#authentication

auth_users = app.config.get('AUTH_USERS', None)
if auth_users:
    authDB = FlaskRealmDigestDB('Route53Realm')

    for user,password in auth_users:
        authDB.add_user(user, password)

    app.wsgi_app = AuthMiddleware(app.wsgi_app, authDB)

import route53.models
