#!/usr/bin/env ipython
from route53 import app

ctx = app.test_request_context()
ctx.push()
