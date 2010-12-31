#!/usr/bin/env ipython
from application import *

ctx = app.test_request_context()
ctx.push()
