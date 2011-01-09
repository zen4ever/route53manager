Route 53 Manager
----------------

Management GUI for Route 53 Amazon Cloud DNS service written in Flask.

How to install
--------------

Clone the project from GitHub

  git clone git@github.com:marpasoft/route53manager.git

Install dependencies

  pip install -r requirements.txt

Create config file

  cp route53/application.cfg.example route53/application.cfg

Add your AWS credentials to newly created "application.cfg"

Create empty database and run development server

  ./create_db.py
  ./runserver.py

Visit http://127.0.0.1:5000/ in your favorite browser
