from functools import wraps
import authdigest
import flask


class FlaskRealmDigestDB(authdigest.RealmDigestDB):
    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            request = flask.request
            if not self.isAuthenticated(request):
                return self.challenge()

            return f(*args, **kwargs)

        return decorated


class AuthMiddleware(object):

    def __init__(self, app, authDB):
        self.app = app
        self.authDB = authDB

    def __call__(self, environ, start_response):
        req = flask.Request(environ)
        if not self.authDB.isAuthenticated(req):
            response = self.authDB.challenge()
            return response(environ, start_response)
        return self.app(environ, start_response)
