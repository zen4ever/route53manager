Route 53 Manager
----------------

Simple GUI for Route 53 Amazon Cloud DNS service written using Flask and
boto.

Features
========

* Create/delete hosted zones
* Create/update/delete records
* Manipulate recordsets
* Stores change log in the SQL database
* Optional Digest Authentication
* Import DNS records from Slicehost one zone at a time
* Clone DNS zone with all rules, but new domain

Route 53 Manager is meant to be running locally, on user's machine, or local
network behind the firewall. It allows you to manage DNS zones and records
for AWS credentials specified in application.cfg
(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

Since you are running the app, you don't need to pass your AWS credentials to
any third party website.

How to install
==============

Clone the project from GitHub

::

  git clone git://github.com/zen4ever/route53manager.git
  cd route53manager

Install dependencies

::

  pip install -r requirements.txt

Create config file

::

  cp route53/application.cfg.example route53/application.cfg

Add your AWS credentials to newly created "application.cfg"

Create empty database and run development server

::

  ./create_db.py
  ./runserver.py

Visit http://127.0.0.1:5000/ in your favorite browser

Authentication
==============

If you want to run Route53Manager on intranet open only to certain users,
you can enable digest authentication. Define AUTH_USERS variable in your
route53/application.cfg like this:

::

  AUTH_USERS = [
    ('admin', 'admin_password'),
    ('test', 'secret_password'),
  ]

FAQ
===

1. Which Python version is supported by route53manager?

   Flask `documentation <http://flask.pocoo.org/docs/installation/#installation>`_ says that Python2.5+ is required. Some of the plugins might use Python 2.6 specific features, so, recommended version is Python 2.6+.

2. How do I make Route53Manager accessible to requests from other machines on
   my local network?

   By default runserver.py spins a local development server which listens to
   127.0.0.1 IP address, which is not accessible from other machines on your
   network. You can use your machine's IP address (e.g. 192.168.1.15) or
   0.0.0.0 in runserver.py

   ::

       app.run(host=0.0.0.0)

   so your dev server will listen to external requests.

   You can also use some other WSGI server like Gunicorn.

   ::

       pip install gunicorn
       gunicorn route53:app -b 0.0.0.0:8000
