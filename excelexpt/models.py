from excelexpt import db
from sqlalchemy.orm import relationship, backref
from werkzeug import generate_password_hash, check_password_hash
from flask_login import current_user

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100))
    #data = db.Column(db.PickleType)
    scenarios = db.relationship('Scenario', backref='user', cascade="all,delete", lazy='dynamic')
  
    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return '<Email %r>' % self.email

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        #return self._user.enabled
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


class Scenario(db.Model):
    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_base = db.Column(db.Boolean)
    data = db.Column(db.PickleType)
    name = db.Column(db.String)
    income_items = db.Column(db.PickleType)
    basic_expenses = db.Column(db.PickleType)
    misc_expenses = db.Column(db.PickleType)
    debt_accounts = db.Column(db.PickleType)
    cash_accounts = db.Column(db.PickleType)

    def __init__(self, data, name, income_items, basic_expenses, misc_expenses, debt_accounts, cash_accounts):
        self.data = data
        self.name = name
        self.income_items = income_items
        self.basic_expenses = basic_expenses
        self.misc_expenses = misc_expenses
        self.debt_accounts = debt_accounts
        self.cash_accounts = cash_accounts
        self.is_base = False

    def __repr__(self):
        return '<Scenario %r>' % self.id

    def is_base_case(self):
        return self.is_base


from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqlamodel import ModelView
from excelexpt import app


## ADMIN ##
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.email == "lhh@admin"

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Scenario, db.session))
## /ADMIN ##