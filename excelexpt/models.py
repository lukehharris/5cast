from excelexpt import db
from sqlalchemy.orm import relationship, backref
from werkzeug import generate_password_hash, check_password_hash
from flask_login import current_user

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100))
    data = db.Column(db.PickleType)
  
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


from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqlamodel import ModelView
from excelexpt import app


## ADMIN ##
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.email == "lhh@admin"

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
## /ADMIN ##