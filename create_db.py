#!/usr/bin/env python
from route53.models import db
db.drop_all()
db.create_all()
