from boto.route53 import Route53Connection

from flask import Module

from flask import url_for, render_template, g,\
        redirect, flash

from route53.decorators import login_required
from route53.forms import ZoneForm

zones = Module(__name__)


@zones.route('/<int:cred_id>')
@login_required
def zones_list(cred_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = Route53Connection(aws_access_key_id=sc.access_key_id.strip(),
                             aws_secret_access_key=sc.secret_access_key.strip())
    response = conn.get_all_hosted_zones()
    zones = response['ListHostedZonesResponse']['HostedZones']
    return render_template('zones/list.html', zones=zones, cred_id=cred_id)


@zones.route('/<int:cred_id>/new', methods=['GET', 'POST'])
@login_required
def zones_new(cred_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = Route53Connection(aws_access_key_id=sc.access_key_id.strip(),
                             aws_secret_access_key=sc.secret_access_key.strip())

    form = ZoneForm()
    if form.validate_on_submit():
        response = conn.create_hosted_zone(
                form.name.data,
                caller_ref="%s-%s-%s" % (form.name.data, cred_id, form.comment.data),
                comment=form.comment.data)

        info = response['CreateHostedZoneResponse']
        
        nameservers = ', '.join(info['DelegationSet']['NameServers'])
        zone_id = info['HostedZone']['Id']

        flash(u"A zone with id %s has been created. Use following nameservers %s"
               % (zone_id, nameservers))

        return redirect(url_for('zones_list', cred_id=cred_id))
    return render_template('zones/new.html', form=form, cred_id=cred_id)
