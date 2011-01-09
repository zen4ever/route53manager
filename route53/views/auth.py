from flask import redirect, Module, url_for

auth = Module(__name__)


@auth.route('/')
def index():
    return redirect(url_for('zones.zones_list'))
