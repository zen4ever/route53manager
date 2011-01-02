from flask import url_for, render_template, g,\
        request, redirect, flash, session, Module

auth = Module(__name__)


@auth.route('/')
def index():
    return render_template('index.html')


@auth.route('/logout')
def logout():
    session.pop('twitter_oauthtok', None)
    session.pop('identity.name', None)
    session.pop('identity.auth_type', None)
    return redirect(url_for('auth.index'))


@auth.route('/login')
def login():
    from route53.oauth import twitter
    if g.identity.name == 'anon':
        return twitter.authorize(callback=url_for('.oauth_authorized',
            next=request.args.get('next') or request.referrer or None))
    else:
        flash(u'You are already logged in with Twitter as %s'
                % g.identity.name)
        return redirect(request.args.get('next') or url_for('auth.index'))
