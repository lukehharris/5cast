import build_ss_in_python
import util_fxns
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, Response, send_from_directory, send_file
from excelexpt import app, db, login_manager
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, AnonymousUser, confirm_login, fresh_login_required
from models import User, Scenario
import json, math

from xlrd import open_workbook
from xlwt import Workbook, easyxf, Formula
from xlwt.Utils import rowcol_to_cell


@app.route('/')
def index():
    #return render_template('test_temp.html')
    return "Under Construction"

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
    if current_user.is_anonymous():
        return redirect(url_for('login'))

    s = current_user.data

    #print 'checkpoint 1'

    try:
        survival_months = "{0:0.1f}".format(s['cash_accounts']['total'][0] / s['expenses']['total'][0])
    except ZeroDivisionError:
        survival_months = 0.0

    if s['net_income'][0] < 0:
        debt_free_months = 'NEVER'
    else:
        debt_free_months = 'X'

    #print 'checkpoint 2'

    total_debt = s['debt_accounts']['total_debt'][0]
    WA_rate = 0
    pmnts_remaining = {}
    total_paid = {}
    first_iter = True
    first_sec = ''
    #print 'checkpoint 3'
    for section in s['debt_accounts']['accounts']:
        beg_balance = s['debt_accounts']['accounts'][section]['items']['beginning_balance'][1]
        #print 'beg_balance ', beg_balance
        rate = s['debt_accounts']['accounts'][section]['rate']
        #print 'rate ', rate
        payment = -1 * s['debt_accounts']['accounts'][section]['items']['payments'][1]
        #print 'payment ',payment
        try:
            WA_rate += (beg_balance / total_debt) * rate
            #print 'WA_rate ',WA_rate
        except ZeroDivisionError:
            WA_rate = 0
        try:
            pmnts_remaining[section] = math.ceil( math.log(1 / (1 - ( (beg_balance * (rate / 12.0) ) / payment) ) ) / math.log(1 + (rate / 12.0) ) )
        except ZeroDivisionError:
            pmnts_remaining[section] = 0
        #print 'pmnts_remaining ', pmnts_remaining
        total_paid[section] = payment * float(pmnts_remaining[section])
        #print 'total_paid ', total_paid
        #print 'checkpoint 4'
        if first_iter:
            first_iter = False
            first_sec = section
            new_sec = 'First +100'
            payment += 100.0
            try:
                pmnts_remaining[new_sec] = math.ceil( math.log(1 / (1 - ( (beg_balance * (rate / 12.0) ) / payment) ) ) / math.log(1 + (rate / 12.0) ) )
            except ZeroDivisionError:
                pmnts_remaining[new_sec] = 0
            total_paid[new_sec] = payment * float(pmnts_remaining[new_sec])

    WA_rate = round(WA_rate * 100, 1)
    
    

    #print 'checkpoint 5'




    return render_template('demo2_output.html', s=s, survival_months=survival_months, debt_free_months=debt_free_months, WA_rate=WA_rate, pmnts_remaining=pmnts_remaining, total_paid=total_paid, first_sec=first_sec)

@app.route('/demo2')
def demo2():
    if current_user.is_active():
        return render_template('demo2.html')
    else:
        return redirect(url_for('login'))



import build_demo3

@app.route('/demo3')
def demo3():
    if current_user.is_active():
        scenarios_query = current_user.scenarios.all()
        
        if scenarios_query == []:
            scenarios = None
            data_exists = False
        else:
            scenarios = []
            for scenario in scenarios_query:
                scenarios.append(scenario.data)
            data_exists = True
        return render_template('demo3.html',data_exists=data_exists,s=scenarios)
    else:
        return redirect(url_for('login'))

@app.route('/submit_demo3', methods=['POST'])
def submit_demo3():
    names = {0:''}
    income  = {0:{}}
    basic_expenses = {0:{}}
    debt_expenses = {0:{}}
    misc_expenses = {0:{}}
    debt_balances = {0:{}}
    cash_balances = {0:{}}
    rates = {0:{}}
    print request.form
    scenarios = []
    for item in request.form:
        print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = 0
        else:
            item_value = request.form[item].replace(",", "")
        prefix = item[:3]
        item_name = item[3:-2]
        scenario = int(item[-1])
        if scenario not in scenarios:
            names.update({scenario:''})
            income.update({scenario:{}})
            basic_expenses.update({scenario:{}})
            debt_expenses.update({scenario:{}})
            misc_expenses.update({scenario:{}})
            debt_balances.update({scenario:{}})
            cash_balances.update({scenario:{}})
            rates.update({scenario:{}})
            scenarios.append(scenario)
        if prefix == "na_":
            names[scenario] = item_value
        elif prefix == "in_":
            income[scenario].update({item_name: item_value})
        elif prefix == "be_":
            basic_expenses[scenario].update({item_name: item_value})
        elif prefix == "de_":
            debt_expenses[scenario].update({item_name: item_value})
        elif prefix == "me_":
            misc_expenses[scenario].update({item_name: item_value})
        elif prefix == "ba_":
            debt_balances[scenario].update({item_name: item_value})
        elif prefix == "cb_":
            cash_balances[scenario].update({item_name: item_value})
        elif prefix == "ra_":
            rates[scenario].update({item_name: float(item_value)/100.0})
    #print rates

    #scenario_count = len(scenarios)

    print 'cash_balances: \n',cash_balances
    print 'rates: \n',rates




    d = build_demo3.build_demo3_data(names, income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates, scenarios)

    if current_user.is_active():
        #remove existing scenarios
        scenarios_query = current_user.scenarios.all()
        for scenario in scenarios_query:
            db.session.delete(scenario)


        for scenario in range(0,len(scenarios)):
        #for scenario in range(0,1):
            new_scenario = Scenario(d[scenario])
            if scenario == 0:
                new_scenario.is_base = True
            current_user.scenarios.append(new_scenario)
        #current_user.data = d[0]
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('demo3_output_detail'))

@app.route('/demo3_output')
def demo3_output():
    if current_user.is_anonymous():
        return redirect(url_for('login'))
    scenarios_query = current_user.scenarios.all()
    scenarios = []
    for scenario in scenarios_query:
        scenarios.append(scenario.data)

    #print scenarios

    ## Chart Data and Labels ##
    Chart1_data_pts = []
    Chart1_labels = []
    for x in range(0,len(scenarios)):
        Chart1_data_pts.append([])
        for y in range(0,len(scenarios[x]['net_worth']),12):
            Chart1_data_pts[x].append(scenarios[x]['net_worth'][y])
        #for k,v in scenarios[x]['net_worth'].iteritems():
        #    Chart1_data_pts[x].append(v)
    for x in range(0,len(scenarios[0]['net_worth']),12):
        Chart1_labels.append(x)


    ## / Chart Data and Labels ##

    #return render_template('demo3_output.html', s=scenarios_query[1].data)
    return render_template('demo3_output.html', s=scenarios,Chart1_data_pts=Chart1_data_pts,Chart1_labels=Chart1_labels)

@app.route('/demo3_output_detail')
def demo3_output_detail():
    if current_user.is_anonymous():
        return redirect(url_for('login'))
    scenarios_query = current_user.scenarios.all()
    scenarios = []
    for scenario in scenarios_query:
        scenarios.append(scenario.data)
    return render_template('demo3_output_detail.html', s=scenarios)


@app.route('/demo4')
def demo4():
    if current_user.is_active():
        scenarios_query = current_user.scenarios.all()
        base_id = None
        other_ids = []
        if scenarios_query == []:
            data_exists = False
        else:
            for scenario in scenarios_query:
                if scenario.is_base:
                    base_id = scenario.id
                else:
                    other_ids.append(scenario.id)
            data_exists = True
        return render_template('demo4.html',data_exists=data_exists, base_id=base_id, other_ids=other_ids)
    else:
        return redirect(url_for('login'))
    
@app.route('/demo5')
def demo5():
    if current_user.is_active():
        scenarios_query = current_user.scenarios.all()
        base_id = None
        other_ids = []
        if scenarios_query == []:
            data_exists = False
        else:
            for scenario in scenarios_query:
                if scenario.is_base:
                    base_id = scenario.id
                else:
                    other_ids.append(scenario.id)
            data_exists = True
        return render_template('demo5.html',data_exists=data_exists, base_id=base_id, other_ids=other_ids)
    else:
        return redirect(url_for('login'))

@app.route('/demo6')
def demo6():
    if current_user.is_active():
        scenarios_query = current_user.scenarios.all()
        base_id = None
        other_ids = []
        if scenarios_query == []:
            data_exists = False
        else:
            for scenario in scenarios_query:
                if scenario.is_base:
                    base_id = scenario.id
                else:
                    other_ids.append(scenario.id)
            data_exists = True
        return render_template('demo6.html',data_exists=data_exists, base_id=base_id, other_ids=other_ids)
    else:
        return redirect(url_for('login'))

@app.route('/demo7')
def demo7():
    if current_user.is_active():
        scenarios_query = current_user.scenarios.all()
        base_id = None
        other_ids = []
        new_data = None
        if scenarios_query == []:
            data_exists = False
            data = {
                'name':'Base Case',
                'isBaseCase': True,
                'income_items': {u'Salary': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}},
                'basic_expenses': {u'TV/Internet': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}, u'Food': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}, u'Housing': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}, u'Utilities': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}, u'Phone': {u'frequency': u'monthly', u'type': u'flatline', u'value':u'0'}, u'Gym': {u'frequency': u'monthly', u'type': u'flatline', u'value': u'0'}},
                'misc_expenses': {},
                'cash_accounts': {u'Checking': {u'rate': u'0', u'balance': u'0'}, u'Savings': {u'rate': u'0', u'balance': u'0'}, u'Investment': {u'rate': u'0', u'balance': u'0'}},
                'debt_accounts': {u'Credit Card': {u'rate': u'0', u'balance': u'0', u'payment': u'0'}, u'Student': {u'rate': u'0', u'balance': u'0', u'payment': u'0'}}
            }
            new_data = build_demo7.build_demo7_data(data)
            new_data = json.dumps(new_data)
        else:
            for scenario in scenarios_query:
                if scenario.is_base:
                    base_id = scenario.id
                else:
                    other_ids.append(scenario.id)
            data_exists = True
        return render_template('demo7.html',data_exists=data_exists,new_data=new_data, base_id=base_id, other_ids=other_ids)
    else:
        return redirect(url_for('login'))

import build_demo7


@app.route('/case', methods=['POST']) #this is where new cases are POSTed, or collections are GET..tten
def case():
    if request.method == 'POST':
        data = {}
        for item in request.json:
            value = request.json[item]
            if item != 'data':
                print item,value
            data.update({item:value})
        #print data
        s = build_demo7.build_demo7_data(data)

        if current_user.is_active():            
            new_scenario = Scenario(s, data['name'], data['income_items'], data['basic_expenses'], data['misc_expenses'], data['debt_accounts'], data['cash_accounts'])
            if data['isBaseCase']:
                new_scenario.is_base = True
            current_user.scenarios.append(new_scenario)
            db.session.add(current_user)
            db.session.flush()
            this_id = new_scenario.id
            db.session.commit()

        data.update({'id':this_id,'data':s})
        return json.dumps(data),200

@app.route('/case/<id_input>', methods=['GET','PUT','DELETE']) #this is where existing cases are saved/deleted to
def case2(id_input):
    if request.method == 'GET':
        data = {}
        if current_user.is_active():
            this_scenario = current_user.scenarios.filter_by(id=id_input).first()
            data['id'] = id_input
            data['data'] = this_scenario.data
            data['isBaseCase'] = this_scenario.is_base
            data['name'] = this_scenario.name
            data['income_items'] = this_scenario.income_items
            data['basic_expenses'] = this_scenario.basic_expenses
            data['misc_expenses'] = this_scenario.misc_expenses
            data['debt_accounts'] = this_scenario.debt_accounts
            data['cash_accounts'] = this_scenario.cash_accounts
        return jsonify(**data),200

    if request.method == 'PUT':
        data = {}
        for item in request.json:
            value = request.json[item]
            if item != 'data':
                print item,value
            data.update({item:value})
        #print data
        s = build_demo7.build_demo7_data(data)

        if current_user.is_active():
            #print data['id']       
            this_scenario = current_user.scenarios.filter_by(id=data['id']).first()
            #print this_scenario
            this_scenario.data = s
            this_scenario.name = data['name']
            this_scenario.income_items = data['income_items']
            this_scenario.basic_expenses = data['basic_expenses']
            this_scenario.misc_expenses = data['misc_expenses']
            this_scenario.debt_accounts = data['debt_accounts']
            this_scenario.cash_accounts = data['cash_accounts']
            db.session.add(this_scenario)
            db.session.commit()        
            
        return json.dumps({'data':s}),200
    
    if request.method == 'DELETE':
        #delete the object with corresponding id. return 200 status
        print 'DELETED CASE NUMBER ',id_input
        if current_user.is_active():
            this_scenario = current_user.scenarios.filter_by(id=id_input).first()
            db.session.delete(this_scenario)
            db.session.commit()
        return '200'
    


@app.route('/example_output')
def example_output():
    email = 'example'
    password = 'example'
    user = util_fxns.authenticate(email, password)
    print user
    login_user(user)

    scenarios_query = user.scenarios.all()
    base_id = None
    other_ids = []
    new_data = None
    for scenario in scenarios_query:
        if scenario.is_base:
            base_id = scenario.id
        else:
            other_ids.append(scenario.id)
    data_exists = True
    return render_template('example_output.html',data_exists=data_exists,new_data=new_data, base_id=base_id, other_ids=other_ids)


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
                return redirect(url_for('demo7'))
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
    return(redirect(url_for('login')))

