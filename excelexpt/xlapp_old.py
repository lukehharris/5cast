from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
#from flask_sqlalchemy import SQLAlchemy
import os
#from flask_login import (LoginManager, current_user, login_required,login_user, logout_user, UserMixin, AnonymousUser,confirm_login, fresh_login_required)
#from sqlalchemy.orm import relationship, backref
#from werkzeug import generate_password_hash, check_password_hash
#from flask_admin import Admin, BaseView, expose
#from flask_admin.contrib.sqlamodel import ModelView

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres://lharris:binaans@localhost/vpflaskdb')
#db = SQLAlchemy(app)

#login_manager = LoginManager()
#login_manager.setup_app(app)

app.secret_key = "DS53DFS3DF\SDF5SDF568SD4F2SD1F\2SD1F32SD1"

##############################
#	Models
##############################
"""
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String)

    def __init__(self, firstname, lastname, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
"""



##############################
#	/Models
##############################


##############################
#	Admin
##############################
"""
class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_active() and current_user.email == "lhh@admin":
            return True
        else:
            return False

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Primer, db.session))
admin.add_view(MyModelView(Venture, db.session))
"""
##############################
#	/Admin
##############################


##############################
#	Views
##############################


from xlrd import open_workbook
from xlwt import Workbook, easyxf, Formula
from xlwt.Utils import rowcol_to_cell

@app.route('/')
def index():

    """
    wb = Workbook()
    s = wb.add_sheet('Model')
    s.write(0,0, 'Personal Finance Model',easyxf('borders: bottom thick;' 'font: bold True, height 320;'))
    s.write(2,1, 'Income:')
    s.write(3,1, 'Salary')
    s.write(3,2, Formula('5*5'))
    s.write(3,3, Formula('C4'))
    s.write(3,4, Formula(rowcol_to_cell(3,3)))


    wb.save('xlwt_ex.xls')
    """

    return render_template('test_temp.html')

@app.route('/pydata')
def pydata():
    return render_template('test_temp2.html')

import util_fxns
from flask import send_from_directory

@app.route('/submit', methods=['POST'])
def submit():
    
    income  = {}
    basic_expenses = {}
    debt_expenses = {}
    misc_expenses = {}
    debt_balances = {}
    cash_balances = {}
    rates = {}
    print request.form
    for item in request.form:
        print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = 0
        else:
            item_value = request.form[item].replace(",", "")
        prefix = item[:3]
        if prefix == "in_":
            income.update({item[3:]: item_value})
        elif prefix == "be_":
            basic_expenses.update({item[3:]: item_value})
        elif prefix == "de_":
            debt_expenses.update({item[3:]: item_value})
        elif prefix == "me_":
            misc_expenses.update({item[3:]: item_value})
        elif prefix == "ba_":
            debt_balances.update({item[3:]: item_value})
        elif prefix == "cb_":
            cash_balances.update({item[3:]: item_value})
        elif prefix == "ra_":
            rates.update({item[3:]: item_value})
    print rates

    util_fxns.build_xls_file(income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates)

    #return render_template('submission_received.html', income=income, basic_expenses=basic_expenses, debt_expenses=debt_expenses, misc_expenses=misc_expenses, balances=balances)

    return send_from_directory('tmp/','xlwt_ex.xls',as_attachment=True,attachment_filename='model.xls')
    
import build_ss_in_python

@app.route('/submit_pydata', methods=['POST'])
def submit_pydata():
    income  = {}
    basic_expenses = {}
    debt_expenses = {}
    misc_expenses = {}
    debt_balances = {}
    cash_balances = {}
    rates = {}
    print request.form
    for item in request.form:
        print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = 0
        else:
            item_value = request.form[item].replace(",", "")
        prefix = item[:3]
        if prefix == "in_":
            income.update({item[3:]: item_value})
        elif prefix == "be_":
            basic_expenses.update({item[3:]: item_value})
        elif prefix == "de_":
            debt_expenses.update({item[3:]: item_value})
        elif prefix == "me_":
            misc_expenses.update({item[3:]: item_value})
        elif prefix == "ba_":
            debt_balances.update({item[3:]: item_value})
        elif prefix == "cb_":
            cash_balances.update({item[3:]: item_value})
        elif prefix == "ra_":
            rates.update({item[3:]: item_value})
    print rates

    s = build_ss_in_python.build_ss(income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates)
    print s

    return render_template('submission_received.html', s=s)

        #, basic_expenses=basic_expenses, debt_expenses=debt_expenses, misc_expenses=misc_expenses, balances=balances)





@app.route('/read')
def read():
    wb = open_workbook('ex1.xlsx')

    for s in wb.sheets():
        print 'Sheet:',s.name
        for row in range(s.nrows):
            values = []
            for col in range(s.ncols):
                values.append(s.cell(row,col).value)
            print ','.join(values)
        print

    return render_template('test_temp.html')


"""
@app.route('/login', methods=['POST'])
def login():
    error = None
    email = None
    password = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print "email: " + email
        user = authenticate(email, password)
        if user:
            if login_user(user):
                #do stuff
                return redirect(url_for('homepage', error=error))
        error = "Login failed"
    #return render_template('login.html', login=True, error=error, email=email, password=password)
    return redirect(url_for('homepage', error=error))


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    email = None
    password = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(email,password)
        db.session.add(user)
        db.session.commit()
        #error = "user account created!"
        return redirect(url_for('login'))
    return render_template('create_account.html', email=email, password=password)



@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    else:
        return None

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(redirect(url_for('homepage')))

def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        if user.check_password(password):
            return user
    return False
"""
##############################
#	/Views
##############################

if __name__ == "__main__":
    app.run(debug=True)