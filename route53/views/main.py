from flask import redirect, Module, url_for

main = Module(__name__)


@main.route('/')
def index():
    return redirect(url_for('zones.zones_list'))
