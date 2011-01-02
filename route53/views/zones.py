from flask import Module

from flask import url_for, render_template, g,\
        redirect, flash, request

from route53.decorators import login_required
from route53.forms import ZoneForm

zones = Module(__name__)


@zones.route('/<int:cred_id>')
@login_required
def zones_list(cred_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = sc.get_connection()
    response = conn.get_all_hosted_zones()
    zones = response['ListHostedZonesResponse']['HostedZones']
    return render_template('zones/list.html', zones=zones, credential=sc)


@zones.route('/<int:cred_id>/new', methods=['GET', 'POST'])
@login_required
def zones_new(cred_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = sc.get_connection()

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
    return render_template('zones/new.html', form=form, credential=sc)


@zones.route('/<int:cred_id>/<zone_id>/delete', methods=['GET', 'POST'])
@login_required
def zones_delete(cred_id, zone_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = sc.get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']

    if request.method == 'POST' and 'delete' in request.form:
        response = conn.delete_hosted_zone(zone_id)

        flash(u"A zone with id %s has been deleted" % zone_id)

        return redirect(url_for('zones_list', cred_id=cred_id))
    return render_template('zones/delete.html', credential=sc, zone_id=zone_id, zone=zone)

@zones.route('/<int:cred_id>/<zone_id>')
@login_required
def zones_detail(cred_id, zone_id):
    from route53.models import AWSCredential
    sc = AWSCredential.query.filter_by(id=cred_id, user_id=g.identity.user.id).first_or_404()
    conn = sc.get_connection()
    resp = conn.get_hosted_zone(zone_id)
    zone = resp['GetHostedZoneResponse']['HostedZone']
    nameservers = resp['GetHostedZoneResponse']['DelegationSet']['NameServers']
    print zone

    return render_template('zones/detail.html',
            credential=sc,
            zone_id=zone_id,
            zone=zone,
            nameservers=nameservers)
