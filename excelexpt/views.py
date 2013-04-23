import build_ss_in_python
import util_fxns
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, Response, send_from_directory, send_file
from excelexpt import app, db, login_manager
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, AnonymousUser, confirm_login, fresh_login_required
from models import User
import json

from xlrd import open_workbook
from xlwt import Workbook, easyxf, Formula
from xlwt.Utils import rowcol_to_cell


@app.route('/')
def index():
    return render_template('test_temp.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/pydata')
def pydata():
    return render_template('test_temp2.html')


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
            rates.update({item[3:]: float(item_value)/100.0})
    print rates

    util_fxns.build_xls_file(income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates)

    #return render_template('debug.html')

    return send_from_directory('tmp/','xlwt_ex.xls',as_attachment=True,attachment_filename='model.xls')
    
import build_ss_in_python

@app.route('/submit_demo2', methods=['POST'])
def submit_demo2():
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
            rates.update({item[3:]: float(item_value)/100.0})
    print rates

    s = build_ss_in_python.build_ss(income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates)
    print s

    if current_user.is_active():
        current_user.data = s
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('demo2_output'))
    

@app.route('/demo2_output')
def demo2_output():
    s = current_user.data

    try:
        survival_months = "{0:0.1f}".format(s['cash_accounts']['total'][0] / s['expenses']['total'][0])
    except ZeroDivisionError:
        survival_months = 0.0

    if s['net_income'][0] < 0:
        debt_free_months = 'NEVER'
    else:
        debt_free_months = 'X'

    return render_template('demo2_output.html', s=s, survival_months=survival_months, debt_free_months=debt_free_months)

@app.route('/demo2')
def demo2():
    if current_user.is_active():
        return render_template('demo2.html')
    else:
        return redirect(url_for('login'))



@app.route('/president')
def president():
    return render_template('president.html')

@app.route('/cannon', methods=['GET', 'POST'])
def cannon():
    return render_template('cannon.html')

@app.route('/cannon/cad', methods=['GET', 'POST'])
def cad():
    return send_from_directory('static/cannon/','Brian Coffey - Pneumatic Cannon Provisional Patent Figures.pdf',as_attachment=True)

@app.route('/cannon/patent', methods=['GET', 'POST'])
def patent():
    return send_from_directory('static/cannon/','Brian Coffey - Pneumatic Cannon Provisional Patent.pdf',as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = None
    password = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = util_fxns.authenticate(email, password)
        if user:
            if login_user(user):
                #do stuff
                return redirect(url_for('demo2'))
        #error = "Login failed"
    return render_template('login.html', login=True, email=email, password=password)

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

        this_user = util_fxns.authenticate(email, password)
        if this_user:
            if login_user(this_user):
                #do stuff
                return redirect(url_for('index'))

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
    return(redirect(url_for('index')))

