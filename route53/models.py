import simplejson

from route53 import app

from flaskext.sqlalchemy import SQLAlchemy

# initialize db
db = SQLAlchemy(app)

# Models


class ChangeBatch(db.Model):
    __tablename__ = "change_batches"

    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.String(255))
    status = db.Column(db.String(255))
    comment = db.Column(db.String(255))

    changes = db.relation("Change", backref="change_batch")


class Change(db.Model):
    __tablename__ = "changes"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    ttl = db.Column(db.String(255))
    multiple = db.Column(db.Boolean, default=False)
    value = db.Column(db.String(255))

    change_batch_id = db.Column(db.Integer, db.ForeignKey("change_batches.id"))

    @property
    def values(self):
        if self.multiple:
            return simplejson.loads(self.value)
        else:
            return [self.value]
