from flask import Module

from flask import url_for, render_template, g,\
        redirect, flash

from route53.decorators import login_required
from route53.forms import AWSCredentialForm

credentials = Module(__name__)


@credentials.route('/new', methods=['GET', 'POST'])
@login_required
def new_credentials():
    from route53.models import db, AWSCredential
    form = AWSCredentialForm()
    if form.validate_on_submit():
        credential = AWSCredential(nickname = form.nickname.data,
                                   access_key_id = form.access_key_id.data,
                                   secret_access_key = form.secret_access_key.data,
                                   user_id = g.identity.user.id)
        db.session.add(credential)
        db.session.commit()
        flash('Your new set of AWS credentials has been saved')
        return redirect(url_for('credentials_list'))
    return render_template('credentials/new.html', form=form)

@credentials.route('/')
@login_required
def credentials_list():
    credentials = g.identity.user.credentials
    return render_template('credentials/list.html', credentials=credentials)
