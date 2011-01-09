try:
    import lxml.etree as etree
except ImportError:
    try:
        import cElementTree as etree
        print "Using cElementTree"
    except ImportError:
        try:
            import elementtree.ElementTree as etree
        except ImportError:
            from xml.etree import ElementTree as etree


NAMESPACE = "{https://route53.amazonaws.com/doc/2010-10-01/}"
RECORDSET_TAG = NAMESPACE + 'ResourceRecordSet'
NAME_TAG = NAMESPACE + 'Name'
TYPE_TAG = NAMESPACE + 'Type'
TTL_TAG = NAMESPACE + 'TTL'
RECORD_TAG = NAMESPACE + 'ResourceRecord'
VALUE_TAG = NAMESPACE + 'Value'
RECORDS_TAG = NAMESPACE + 'ResourceRecords'


def render_change_batch(context):
    from route53 import app
    template = app.jinja_env.get_template('xml/change_batch.xml')
    rendered_xml = template.render(context)
    return rendered_xml
