from flaskext import wtf
from flaskext.wtf import validators

class AWSCredentialForm(wtf.Form):
    nickname = wtf.TextField('Nickname', validators=[validators.Required()])
    access_key_id = wtf.TextField('Access Key ID', validators=[validators.Required()])
    secret_access_key = wtf.TextField('Secret Access Key', validators=[validators.Required()])


class ZoneForm(wtf.Form):
    name = wtf.TextField('Domain Name', validators=[validators.Required()])
    comment = wtf.TextAreaField('Comment')
