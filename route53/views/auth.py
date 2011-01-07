from flask import render_template, Module

auth = Module(__name__)


@auth.route('/')
def index():
    return render_template('index.html')
