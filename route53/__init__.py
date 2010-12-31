from flask import Flask

from flaskext.principal import Principal

app = Flask(__name__)

# load configuration
app.config.from_pyfile('application.cfg')

principals = Principal(app)


import route53.views, route53.models, route53.oauth
