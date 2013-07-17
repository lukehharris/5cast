from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://lharris:binaans@localhost/modelbuilderdb')
db = SQLAlchemy(app)

if os.environ.get('DATABASE_URL'):
	PRODUCTION = True
else:
	PRODUCTION = False

login_manager = LoginManager()
login_manager.setup_app(app)

app.secret_key = "DS53GFS3DF\SDF5SDF658DS5F2SD1F\2SD1F32SD1"


##set this up with sendgrid. example here: https://github.com/jbalogh/github-notifications/blob/master/app.py
"""
ADMINS = ['lukehharris@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@modelbuilder.com',
                               ADMINS, 'ModelBuilder Failed')
    mail_handler.setLevel(logging.ERROR)

    from logging import Formatter
    mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))

    app.logger.addHandler(mail_handler)
"""
import excelexpt.views

    