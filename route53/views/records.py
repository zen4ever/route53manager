from flask import Module, redirect, url_for, render_template

from route53.forms import RecordForm
from route53.connection import get_connection


records = Module(__name__)

@records.route('/<zone_id>/new', methods=['GET', 'POST'])
def records_new(zone_id):
    from route53 import app
    from route53.models import ChangeBatch, Change, db
    conn = get_connection()
    zone = conn.get_hosted_zone(zone_id)['GetHostedZoneResponse']['HostedZone']
    form = RecordForm()
    if form.validate_on_submit():
        change_batch = ChangeBatch(change_id='', status='created', comment=form.comment.data)
        db.session.add(change_batch)
        change = Change(action="CREATE",
                        name=form.name.data,
                        type=form.record_type.data,
                        ttl=form.ttl.data,
                        value=form.value.data,
                        change_batch_id=change_batch.id)
        db.session.add(change)
        template = app.jinja_env.get_template('xml/change_batch.xml')
        rendered_xml = template.render({'changes': [change], 'comment': change_batch.comment})
        resp = conn.change_rrsets(zone_id, rendered_xml)
        change_id =  resp['ChangeResourceRecordSetsResponse']['ChangeInfo']['Id'][8:]
        change_batch.change_id = change_id
        change_batch.status = resp['ChangeResourceRecordSetsResponse']['ChangeInfo']['Status']
        db.session.commit()
        return redirect(url_for('zones.zones_records', zone_id=zone_id))
    return render_template('records/new.html', form=form, zone=zone, zone_id=zone_id)
