from boto.route53 import Route53Connection


def get_connection():
    from route53 import app
    return Route53Connection(aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
             aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])
