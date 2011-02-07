from boto.route53.exception import DNSServerError
from flask import Module

from flask import url_for, render_template, \
        redirect, flash, request

from route53.forms import ZoneForm
from route53.xmltools import etree
from route53.connection import get_connection

zones = Module(__name__)


@zones.route('/')
def zones_list():
    conn = get_connection()
    response = conn.get_all_hosted_zones()
    zones = response['ListHostedZonesResponse']['HostedZones']
    return render_template('zones/list.html', zones=zones)


@zones.route('/new', methods=['GET', 'POST'])
def zones_new():
    conn = get_connection()

    form = ZoneForm()
    if form.validate_on_submit():
        response = conn.create_hosted_zone(
                form.name.data,
                comment=form.comment.data)

        info = response['CreateHostedZoneResponse']

        nameservers = ', '.join(info['DelegationSet']['NameServers'])
        zone_id = info['HostedZone']['Id']

        flash(u"A zone with id %s has been created. "
              u"Use following nameservers %s"
               % (zone_id, nameservers))

        return redirect(url_for('zones_list'))
    return render_template('zones/new.html', form=form)


@zones.route('/<zone_id>/delete', methods=['GET', 'POST'])
def zones_delete(zone_id):
    conn = get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']

    error = None

    if request.method == 'POST' and 'delete' in request.form:
        try:
            conn.delete_hosted_zone(zone_id)

            flash(u"A zone with id %s has been deleted" % zone_id)

            return redirect(url_for('zones_list'))
        except DNSServerError as error:
            error = error
    return render_template('zones/delete.html',
                           zone_id=zone_id,
                           zone=zone,
                           error=error)


@zones.route('/<zone_id>')
def zones_detail(zone_id):
    conn = get_connection()
    resp = conn.get_hosted_zone(zone_id)
    zone = resp['GetHostedZoneResponse']['HostedZone']
    nameservers = resp['GetHostedZoneResponse']['DelegationSet']['NameServers']

    return render_template('zones/detail.html',
            zone_id=zone_id,
            zone=zone,
            nameservers=nameservers)


@zones.route('/<zone_id>/records')
def zones_records(zone_id):
    conn = get_connection()
    resp = conn.get_hosted_zone(zone_id)
    zone = resp['GetHostedZoneResponse']['HostedZone']

    record_resp = conn.get_all_rrsets(zone_id)

    from route53.xmltools import RECORDSET_TAG, NAME_TAG, TYPE_TAG, \
            TTL_TAG, RECORDS_TAG, RECORD_TAG, VALUE_TAG

    return render_template('zones/records.html',
            zone_id=zone_id,
            zone=zone,
            recordsets=record_resp)
