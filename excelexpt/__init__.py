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

app.secret_key = "DS53DFS3DF\SDF5SDF658DS5F2SD1F\2SD1F32SD1"


import excelexpt.views

    