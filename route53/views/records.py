from boto.route53.exception import DNSServerError
from flask import Module, redirect, url_for, render_template, request, abort

from route53.forms import RecordForm
from route53.connection import get_connection
from route53.xmltools import render_change_batch


records = Module(__name__)


@records.route('/<zone_id>/new', methods=['GET', 'POST'])
def records_new(zone_id):
    from route53.models import ChangeBatch, Change, db
    conn = get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']
    form = RecordForm()
    error = None
    if form.validate_on_submit():
        change_batch = ChangeBatch(change_id='',
                                   status='created',
                                   comment=form.comment.data)
        db.session.add(change_batch)
        change = Change(action="CREATE",
                        name=form.name.data,
                        type=form.type.data,
                        ttl=form.ttl.data,
                        values=form.values,
                        change_batch_id=change_batch.id)
        db.session.add(change)
        rendered_xml = render_change_batch({'changes': [change],
                                            'comment': change_batch.comment})
        try:
            resp = conn.change_rrsets(zone_id, rendered_xml)
            change_batch.process_response(resp)
            db.session.commit()
            return redirect(url_for('zones.zones_records', zone_id=zone_id))
        except DNSServerError as error:
            error = error
            db.session.rollback()
    return render_template('records/new.html',
                           form=form,
                           zone=zone,
                           zone_id=zone_id,
                           error=error)


def get_record_fields():
    fields = ['name', 'type', 'ttl']
    val_dict = {}
    for field in fields:
        if request.method == "GET":
            result = request.args.get(field, None)
        elif request.method == "POST":
            result = request.form.get("data_"+field, None)
        if result is None:
            abort(404)
        val_dict[field] = result
    return val_dict


@records.route('/<zone_id>/delete', methods=['GET', 'POST'])
def records_delete(zone_id):
    from route53.models import ChangeBatch, Change, db
    conn = get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']
    val_dict = get_record_fields()

    if request.method == "GET":
        values = request.args.getlist('value')
        if not values:
            abort(404)

    error = None
    if request.method == "POST":
        change_batch = ChangeBatch(change_id='', status='created', comment='')
        db.session.add(change_batch)
        values = request.form.getlist('data_value')
        change = Change(action="DELETE",
                        change_batch_id=change_batch.id,
                        values=values,
                        **val_dict)
        db.session.add(change)
        rendered_xml = render_change_batch({'changes': [change],
                                            'comment': change_batch.comment})
        try:
            resp = conn.change_rrsets(zone_id, rendered_xml)
            change_batch.process_response(resp)
            db.session.commit()
            return redirect(url_for('zones.zones_records', zone_id=zone_id))
        except DNSServerError as error:
            error = error
    return render_template('records/delete.html',
                           val_dict=val_dict,
                           values=values,
                           zone=zone,
                           zone_id=zone_id,
                           error=error)


@records.route('/<zone_id>/update', methods=['GET', 'POST'])
def records_update(zone_id):
    from route53.models import ChangeBatch, Change, db
    conn = get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']
    val_dict = get_record_fields()

    if request.method == "GET":
        values = request.args.getlist('value')
        if not values:
            abort(404)
        initial_data = dict(val_dict)
        initial_data['value'] = ';'.join(values)
        form = RecordForm(**initial_data)

    error = None
    if request.method == "POST":
        form = RecordForm()
        change_batch = ChangeBatch(change_id='', status='created', comment=form.comment.data)
        db.session.add(change_batch)
        values = request.form.getlist('data_value')
        delete_change = Change(action="DELETE",
                               change_batch_id=change_batch.id,
                               values=values,
                               **val_dict)
        create_change = Change(action="CREATE",
                               change_batch_id=change_batch.id,
                               values=form.values,
                               type=form.type.data,
                               ttl=form.ttl.data,
                               name=form.name.data)
        db.session.add(delete_change)
        db.session.add(create_change)
        rendered_xml = render_change_batch({'changes': [delete_change, create_change],
                                            'comment': change_batch.comment})
        try:
            resp = conn.change_rrsets(zone_id, rendered_xml)
            change_batch.process_response(resp)
            db.session.commit()
            return redirect(url_for('zones.zones_records', zone_id=zone_id))
        except DNSServerError as error:
            error = error
    return render_template('records/update.html',
                           val_dict=val_dict,
                           values=values,
                           form=form,
                           zone=zone,
                           zone_id=zone_id,
                           error=error)
