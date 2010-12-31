from flask import url_for, render_template, g,\
        request, redirect, flash, session

from flaskext.principal import Identity, identity_changed, \
        identity_loaded

from route53 import app
from route53.decorators import login_required
from route53.oauth import twitter
from route53.models import db, User, AWSCredential
from route53.forms import AWSCredentialForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('twitter_oauthtok', None)
    session.pop('identity.name', None)
    session.pop('identity.auth_type', None)
    return redirect(url_for('index'))


@app.route('/login')
def login():
    if g.identity.name == 'anon':
        return twitter.authorize(callback=url_for('oauth_authorized',
            next=request.args.get('next') or request.referrer or None))
    else:
        flash(u'You are already logged in with Twitter as %s'
                % g.identity.name)
        return redirect(request.args.get('next') or url_for('index'))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    username = resp['screen_name']

    user = User.query.filter_by(username=username).first()

    if not user:
        user = User(username, resp['oauth_token'], resp['oauth_token_secret'])
        db.session.add(user)
        db.session.commit()

    flash('You were signed in as %s' % username)

    identity_changed.send(app, identity=Identity(username))
    return redirect(next_url)


@app.route('/credentials/new', methods=['GET', 'POST'])
@login_required
def new_credentials():
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

@app.route('/credentials/')
@login_required
def credentials_list():
    credentials = g.identity.user.credentials
    return render_template('credentials/list.html', credentials=credentials)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    user = User.query.filter_by(username=identity.name).first()
    identity.user = user
