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


class ZoneForm(wtf.Form):
    name = wtf.TextField('Domain Name', validators=[validators.Required()])
    comment = wtf.TextAreaField('Comment')


class RecordForm(wtf.Form):
    type = wtf.SelectField("Type", choices=RECORD_CHOICES)
    name = wtf.TextField("Name", validators=[validators.Required()])
    value = wtf.TextField("Value", validators=[validators.Required()])
    ttl = wtf.IntegerField("TTL", default="86400",
            validators=[validators.Required()])
    comment = wtf.TextAreaField("Comment")

    @property
    def values(self):
        if self.type.data != 'TXT':
            return filter(lambda x: x,
                      map(lambda x: x.strip(),
                          self.value.data.strip().split(';')))
        else:
            return [self.value.data.strip()]

class RecordAliasForm(wtf.Form):
    type = wtf.SelectField("Type", choices=RECORD_CHOICES)
    name = wtf.TextField("Name", validators=[validators.Required()])
    alias_hosted_zone_id = wtf.TextField("Alias hosted zone ID", validators=[validators.Required()])
    alias_dns_name = wtf.TextField("Alias DNS name", validators=[validators.Required()])
    ttl = wtf.IntegerField("TTL", default="86400",
            validators=[validators.Required()])
    comment = wtf.TextAreaField("Comment")

class APIKeyForm(wtf.Form):
    key = wtf.TextField('API Key', validators=[validators.Required()])
