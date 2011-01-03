from flaskext import wtf
from flaskext.wtf import validators

RECORD_CHOICES = [
    ('A', 'A'),
    ('AAAA', 'AAAA'),
    ('CNAME', 'CNAME'),
    ('MX', 'MX'),
    ('NS', 'NS'),
    ('PTR', 'PTR'),
    ('SOA', 'SOA'),
    ('SPF', 'SPF'),
    ('SRV', 'SRV'),
    ('TXT', 'TXT'),
]


class AWSCredentialForm(wtf.Form):
    nickname = wtf.TextField('Nickname', validators=[validators.Required()])
    access_key_id = wtf.TextField('Access Key ID',
            validators=[validators.Required()])
    secret_access_key = wtf.TextField('Secret Access Key',
            validators=[validators.Required()])


class ZoneForm(wtf.Form):
    name = wtf.TextField('Domain Name', validators=[validators.Required()])
    comment = wtf.TextAreaField('Comment')


class RecordForm(wtf.Form):
    record_type = wtf.SelectField("Type", choices=RECORD_CHOICES)
    name = wtf.TextField("Name", validators=[validators.Required()])
    data = wtf.TextField("Data", validators=[validators.Required()])
    aux_info = wtf.TextField("Auxiliary Info")
    ttl = wtf.IntegerField("TTL", default="86400",
            validators=[validators.Required()])
