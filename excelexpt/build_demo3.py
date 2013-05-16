
def build_demo3_data(names, income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates, scenario_count):
    d = []
    for scenario in range(0,scenario_count):
        s = {'name': names[scenario]}
        #for column indicies, 0 = today, 1 = 1 month from today,...,n=n months from today
        print income
        print income[scenario]
        s = build_income_section(s, income[scenario])
     
        s = build_expense_section(s, basic_expenses[scenario], debt_expenses[scenario], misc_expenses[scenario])
        
        s = calculate_net_income(s)
        
        s = build_cash_section(s, cash_balances[scenario], rates[scenario])
        
        s = build_debt_section(s, debt_balances[scenario], rates[scenario])

        s = calculate_net_worth(s) 

        d.append(s)
    print s['income']
    return d


def build_income_section(s, income):
    s.update({'income': {'items': {}, 'total': {}}})
    for k,v in income.iteritems():
        s['income']['items'].update({k:{0:float(v)}})
        #print s

        fill_value = s['income']['items'][k][0]
        for x in range(1,121):
            s['income']['items'][k][x] = fill_value

    for x in range(0,121):
        s['income']['total'].update({x:0})
        for k in s['income']['items']:
            s['income']['total'][x] += s['income']['items'][k][x]
    #print s
    return s

def build_expense_section(s, basic_expenses, debt_expenses, misc_expenses):
    s.update({'expenses':{'sections':{},'total':{}}})
    s = build_expense_subsection(s, basic_expenses, 'Basic')
    #print s
    s = build_expense_subsection(s, debt_expenses, 'Debt')
    s = build_expense_subsection(s, misc_expenses, 'Misc')
    
    s = sum_expenses(s)

    return s

def build_expense_subsection(s, expense_dict, name):
    s['expenses']['sections'].update({name:{'items':{},'total':{}}})
    for k,v in expense_dict.iteritems():
        s['expenses']['sections'][name]['items'].update({k:{0:float(v)}})

        fill_value = s['expenses']['sections'][name]['items'][k][0]
        for x in range(1,121):
            s['expenses']['sections'][name]['items'][k][x] = fill_value

    for x in range(0,121):
        s['expenses']['sections'][name]['total'].update({x:0})
        for k in s['expenses']['sections'][name]['items']:
            s['expenses']['sections'][name]['total'][x] += s['expenses']['sections'][name]['items'][k][x]

    return s

def sum_expenses(s):
    for x in range(0,121):
        s['expenses']['total'].update({x:0})
        for section in s['expenses']['sections']:
            s['expenses']['total'][x] += s['expenses']['sections'][section]['total'][x]

    return s
    
def calculate_net_income(s):
    s.update({'net_income':{}})
    for x in range(0,121):
        net_income = s['income']['total'][x] - s['expenses']['total'][x]
        s['net_income'].update({x:net_income})

    return s

def build_cash_section(s, cash_balances, rates):
    s['cash_accounts'] = {'accounts':{},'total':{}}
    for k,balance in cash_balances.iteritems():
        name = k[:-8]
        s['cash_accounts']['accounts'].update({name:{'rate':float(rates[name]),'items': {'beginning_balance':{},'withdrawal':{},'interest':{},'ending_balance':{0:float(balance)} } } } )
        s = build_cash_sub_section(s, name)

    s = build_cash_summary(s)

    return s

def build_cash_sub_section(s, name):
    if name == 'Checking':
        #s['cash_accounts']['accounts'][name]['items'].update({'net_income':{0:''}})
        s['cash_accounts']['accounts'][name]['items'].update({'net_income':{0:0}})

    rate = s['cash_accounts']['accounts'][name]['rate']
    
    #s['cash_accounts']['accounts'][name]['items']['beginning_balance'][0] = ''
    #s['cash_accounts']['accounts'][name]['items']['withdrawal'][0] = ''
    #s['cash_accounts']['accounts'][name]['items']['interest'][0] = ''
    
    s['cash_accounts']['accounts'][name]['items']['beginning_balance'][0] = 0
    s['cash_accounts']['accounts'][name]['items']['withdrawal'][0] = 0
    s['cash_accounts']['accounts'][name]['items']['interest'][0] = 0

    for x in range(1,121):
        prev_ending_balance = s['cash_accounts']['accounts'][name]['items']['ending_balance'][x-1]
        s['cash_accounts']['accounts'][name]['items']['beginning_balance'][x] = prev_ending_balance
        s['cash_accounts']['accounts'][name]['items']['withdrawal'][x] = 0
        s['cash_accounts']['accounts'][name]['items']['interest'][x] = prev_ending_balance * (rate/12.0)
        if name == 'Checking':
            s['cash_accounts']['accounts'][name]['items']['net_income'][x] = s['net_income'][x]
            s['cash_accounts']['accounts'][name]['items']['ending_balance'][x] = s['cash_accounts']['accounts'][name]['items']['beginning_balance'][x] - s['cash_accounts']['accounts'][name]['items']['withdrawal'][x] + s['cash_accounts']['accounts'][name]['items']['interest'][x] + s['cash_accounts']['accounts'][name]['items']['net_income'][x]
        else:
            s['cash_accounts']['accounts'][name]['items']['ending_balance'][x] = s['cash_accounts']['accounts'][name]['items']['beginning_balance'][x] - s['cash_accounts']['accounts'][name]['items']['withdrawal'][x] + s['cash_accounts']['accounts'][name]['items']['interest'][x]

    return s

def build_cash_summary(s):
    for x in range (0,121):
        s['cash_accounts']['total'].update({x:0})
        for k,v in s['cash_accounts']['accounts'].iteritems():
            s['cash_accounts']['total'][x] += s['cash_accounts']['accounts'][k]['items']['ending_balance'][x]

    return s

def build_debt_section(s, debt_balances, rates):
    s['debt_accounts'] = {'accounts':{},'total_debt':{},'debt_expense_summary':{}}
    for k,balance in debt_balances.iteritems():
        name = k[:-8]
        s['debt_accounts']['accounts'].update({name:{'rate':float(rates[name]),'items': {'beginning_balance':{},'payments':{},'interest':{},'ending_balance':{0:float(balance)} } } } )
        s = build_debt_sub_section(s, name)

    s = build_debt_summary(s)

    return s

def build_debt_sub_section(s, name):
    rate = s['debt_accounts']['accounts'][name]['rate']
    s['debt_accounts']['accounts'][name]['items']['beginning_balance'][0] = 0
    s['debt_accounts']['accounts'][name]['items']['payments'][0] = 0
    s['debt_accounts']['accounts'][name]['items']['interest'][0] = 0
    for x in range(1,121):
        prev_ending_balance = s['debt_accounts']['accounts'][name]['items']['ending_balance'][x-1]
        s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] = prev_ending_balance
        s['debt_accounts']['accounts'][name]['items']['payments'][x] = (-1) * s['expenses']['sections']['Debt']['items'][name][x]
        s['debt_accounts']['accounts'][name]['items']['interest'][x] = prev_ending_balance * (rate/12.0)

        s['debt_accounts']['accounts'][name]['items']['ending_balance'][x] = s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x] + s['debt_accounts']['accounts'][name]['items']['interest'][x]

    return s

def build_debt_summary(s):
    s['debt_accounts']['debt_expense_summary'].update({'interest_paid':{},'principal_paid':{},'total_expense':{}})

    for x in range (0,121):
        s['debt_accounts']['total_debt'].update({x:0})
        for k,v in s['debt_accounts']['accounts'].iteritems():
            s['debt_accounts']['total_debt'][x] += s['debt_accounts']['accounts'][k]['items']['ending_balance'][x]

    for x in range(0,121):
        s['debt_accounts']['debt_expense_summary']['interest_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['interest_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x]

    for x in range(0,121):
        s['debt_accounts']['debt_expense_summary']['principal_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['principal_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x]
        s['debt_accounts']['debt_expense_summary']['principal_paid'][x] = -(s['debt_accounts']['debt_expense_summary']['principal_paid'][x])

    for x in range(0,121):
        s['debt_accounts']['debt_expense_summary']['total_expense'].update({x:0})
        s['debt_accounts']['debt_expense_summary']['total_expense'][x] = s['debt_accounts']['debt_expense_summary']['interest_paid'][x] + s['debt_accounts']['debt_expense_summary']['principal_paid'][x]

    return s

def calculate_net_worth(s):
    s.update({'net_worth':{}})
    for x in range (0,121):
        s['net_worth'].update({x:0})
        s['net_worth'][x] = s['cash_accounts']['total'][x] - s['debt_accounts']['total_debt'][x]

    return s
