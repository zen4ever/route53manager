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
