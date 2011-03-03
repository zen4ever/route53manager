from boto.route53.exception import DNSServerError
from functools import wraps
from itertools import groupby

from flask import Module, session, redirect, url_for, render_template, request

from pyactiveresource.activeresource import ActiveResource

from route53.connection import get_connection
from route53.forms import APIKeyForm
from route53.xmltools import render_change_batch

slicehost = Module(__name__)

API_KEY = 'slicehost_api_key'
API_URL = 'https://%s@api.slicehost.com/'


def get_zone_class():
    class Zone(ActiveResource):
        _site = API_URL % session[API_KEY]
    return Zone


def get_record_class():
    class Record(ActiveResource):
        _site = API_URL % session[API_KEY]
    return Record


def requires_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not API_KEY in session:
            return redirect(url_for('slicehost.index'))
        return f(*args, **kwargs)
    return decorated


@slicehost.route('/', methods=['GET', 'POST'])
def index():
    if 'clean' in request.args:
        del session[API_KEY]
    if API_KEY in session:
        return redirect(url_for('slicehost.zones'))
    form = APIKeyForm()
    if form.validate_on_submit():
        session[API_KEY] = form.key.data
        return redirect(url_for('slicehost.zones'))
    return render_template('slicehost/index.html', form=form)


@slicehost.route('/zones')
@requires_key
def zones():
    Zone = get_zone_class()
    zones = Zone.find()
    return render_template('slicehost/zones.html', zones=zones)


@slicehost.route('/zones/<zone_id>')
@requires_key
def records(zone_id):
    Zone = get_zone_class()
    zone = Zone.find(zone_id)
    Record = get_record_class()
    records = Record.find(zone_id=zone_id)
    records = sorted(records, key=lambda x: x.record_type)
    results = []
    for k, g in groupby(records, key=lambda x: (x.record_type, x.name)):
        record_type, name = k
        results.append((record_type, name, list(g)))
    return render_template('slicehost/records.html', zone=zone, records=results)


@slicehost.route('/zones/<zone_id>/import', methods=['GET', 'POST'])
@requires_key
def import_zone(zone_id):
    from route53.models import ChangeBatch, Change, db

    Zone = get_zone_class()
    zone = Zone.find(zone_id)
    Record = get_record_class()

    # filter out NS records
    records = filter(lambda x: x.record_type != 'NS', Record.find(zone_id=zone_id))

    records = sorted(records, key=lambda x: x.record_type)

    # order records by record_type and name into recordsets

    conn = get_connection()
    response = conn.create_hosted_zone(zone.origin)
    info = response['CreateHostedZoneResponse']
    new_zone_id = info['HostedZone']['Id']

    errors = []

    for k, g in groupby(records, key=lambda x: (x.record_type, x.name)):
        change_batch = ChangeBatch(change_id='',
                                   status='created',
                                   comment='')

        db.session.add(change_batch)
        record_type, name = k
        rcds = list(g)
        record_name = zone.origin in name and name or name + "." + zone.origin
        change = Change(action="CREATE",
                        name=record_name,
                        type=record_type,
                        ttl=rcds[0].ttl,
                        values=map(lambda x: x.data, rcds),
                        change_batch_id=change_batch.id)
        db.session.add(change)
        changes = [change]

        rendered_xml = render_change_batch({'changes': changes, 'comment': ''})

        try:
            from route53 import shortid
            resp = conn.change_rrsets(shortid(new_zone_id), rendered_xml)
            change_batch.process_response(resp)
            db.session.commit()
        except DNSServerError as error:
            errors.append((record_type, name, error))
            db.session.rollback()

    if errors:
        return render_template('slicehost/import_zone.html',
                errors=errors,
                zone=zone)

    return redirect(url_for('main.index'))
