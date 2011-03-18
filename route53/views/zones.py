from boto.route53.exception import DNSServerError
from flask import Module

from flask import url_for, render_template, \
        redirect, flash, request

from route53.forms import ZoneForm
from route53.connection import get_connection

from route53.xmltools import render_change_batch

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

    return render_template('zones/records.html',
            zone_id=zone_id,
            zone=zone,
            recordsets=record_resp)


@zones.route('/clone/<zone_id>', methods=['GET', 'POST'])
def zones_clone(zone_id):
    conn = get_connection()

    zone_response = conn.get_hosted_zone(zone_id)
    original_zone = zone_response['GetHostedZoneResponse']['HostedZone']

    form = ZoneForm()
    errors = []

    if form.validate_on_submit():
        response = conn.create_hosted_zone(
                form.name.data,
                comment=form.comment.data)

        info = response['CreateHostedZoneResponse']

        nameservers = ', '.join(info['DelegationSet']['NameServers'])

        new_zone_id = info['HostedZone']['Id']

        original_records = conn.get_all_rrsets(zone_id)

        from route53.models import ChangeBatch, Change, db

        for recordset in original_records:
            if not recordset.type in ["SOA", "NS"]:

                print recordset.type

                change_batch = ChangeBatch(change_id='',
                                           status='created',
                                           comment='')
                db.session.add(change_batch)
                change = Change(action="CREATE",
                                name=recordset.name.replace(original_zone['Name'],
                                                            form.name.data),
                                type=recordset.type,
                                ttl=recordset.ttl,
                                values = recordset.resource_records,
                                change_batch_id=change_batch.id)

                db.session.add(change)
                changes = [change]

                rendered_xml = render_change_batch({'changes': changes, 'comment': ''})

                print rendered_xml

                try:
                    from route53 import shortid
                    resp = conn.change_rrsets(shortid(new_zone_id), rendered_xml)
                    change_batch.process_response(resp)
                    db.session.commit()
                except DNSServerError as error:
                    errors.append((recordset.type, recordset.name, error))
                    db.session.rollback()

        if not errors:
            flash(u"A zone with id %s has been created. "
                  u"Use following nameservers %s"
                   % (new_zone_id, nameservers))
            return redirect(url_for('zones_list'))

    return render_template('zones/clone.html',
        form=form, errors=errors, original_zone=original_zone)
