from flask import Flask

from flaskext.principal import Principal

from route53.views.credentials import credentials
from route53.views.zones import zones
from route53.views.auth import auth

app = Flask(__name__)
app.register_module(auth)
app.register_module(credentials, url_prefix='/credentials')
app.register_module(zones, url_prefix='/zones')

# load configuration
app.config.from_pyfile('application.cfg')

principals = Principal(app)


@app.template_filter('shortid')
def shortid(s):
    return s.replace('/hostedzone/', '')

import route53.models, route53.oauth
