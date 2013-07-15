import math

global_max_months = 121

def build_demo7_data(data):
    
    s = {'name': data['name']}
    #for column indicies, 0 = today, 1 = 1 month from today,...,n=n months from today

    s = build_income_section(s, data['income_items'])

    debt_expenses = {}
    for name,value in data['debt_accounts'].iteritems():
        debt_expenses[name] = {'type':'flatline','frequency':'monthly','value':value['payment']}
 
    s = build_expense_section(s, data['basic_expenses'], debt_expenses, data['misc_expenses'])
    s = calculate_net_income(s)
    s = calc_net_income_raw(s)
    s = build_cash_section(s, data['cash_accounts'])
    print 'cp 1'
    s = build_debt_section(s, data['debt_accounts'])
    s = calculate_net_worth(s) 
    s = calculate_totals(s)
    
    s = calc_survival_period_2(s)

    s,iterations = build_debt_summary(s, min_payment=True)
    s,NI_order = allocate_NI_2(s)
    s = calc_insolvency(s)
    if s['insolvent'] == True:
        s = calc_survival_period_2(s, deduction="Net Income")
    else:
        s = NI_allocation_introspection(s, NI_order)

    s, iterations = build_debt_summary(s, min_payment=False, iterations=iterations)

    return s

def calc_insolvency(s):
    # insolvency = assets < 0
    s.update({'insolvent':False})
    for x in range(1,global_max_months):
        if s['cash_accounts']['total'][x] < 0:
            s['insolvent'] = True
    return s

def calc_survival_period(s):
    expenses = s['expenses']['total'][0]
    #print expenses
    total_assets = s['cash_accounts']['total'][0]
    #print total_assets
    try:
        survival_period_unround = total_assets / expenses
        survival_period = round(survival_period_unround,1)
    except ZeroDivisionError:
        survival_period = 'no expenses'
        survival_period_unround = 0
    #print survival_period
    s.update({'survival_period':{'months_remaining':survival_period,'months_remaining_rounded':int(math.ceil(survival_period_unround)),'beginning_balance':{0:0},'expenses':{0:0},'ending_balance':{0:0}}})
    
    s['survival_period']['ending_balance'][0] = s['cash_accounts']['total'][0]
    for x in range(1,int(math.ceil(survival_period_unround))+1):
        s['survival_period']['beginning_balance'][x] = s['survival_period']['ending_balance'][x-1]
        s['survival_period']['expenses'][x] = -1* expenses
        s['survival_period']['ending_balance'][x] = s['survival_period']['beginning_balance'][x] + s['survival_period']['expenses'][x]

    return s

def calc_survival_period_2(s, deduction='Expenses'):
    s.update({'survival_period':{'months_remaining':0,'months_remaining_rounded':0,'deduction':deduction,'beginning_balance':{0:0},'expenses':{0:0},'ending_balance':{0:s['cash_accounts']['total'][0]}}})

    x = 1
    while x < 121:
        s['survival_period']['beginning_balance'][x] = s['survival_period']['ending_balance'][x-1]

        if deduction == 'Expenses':
            s['survival_period']['expenses'][x] = -1* s['expenses']['total'][x]
        elif deduction == 'Net Income':
            s['survival_period']['expenses'][x] = s['net_income'][x]


        s['survival_period']['ending_balance'][x] = s['survival_period']['beginning_balance'][x] + s['survival_period']['expenses'][x]

        if s['survival_period']['ending_balance'][x] <= 0:
            s['survival_period']['months_remaining_rounded'] = x
            try:
                survival_period = (x-1) + ((s['survival_period']['beginning_balance'][x]) / (-1*s['survival_period']['expenses'][x]))
            except ZeroDivisionError:
                survival_period = 0
            s['survival_period']['months_remaining'] = round(survival_period,1)
            break
        else:
            x += 1
    if x == 121:
        s['survival_period']['months_remaining'] = ">10"
    return s

def calc_net_income_raw(s):
    s.update({'net_income_raw':{0:0}})
    for x in range(0,global_max_months):
        s['net_income_raw'][x] = s['net_income'][x]
        for k,v in s['expenses']['sections']['Debt']['items'].iteritems():
            if k[-9:] == '_Optional':
                s['net_income_raw'][x] +=  v[x]
    return s

"""
def allocate_NI(q, NI_order):
    s = q #need this for calculate_totals_for_x() to receive the return value properly
    current_col = 1
    carryover_NI = 0
    for item in NI_order:
        account_type = item['type']
        account_name = item['name']
        #if s['net_income'] > 0:
        try:
            NI_test = s[account_type]['accounts'][account_name]['items']['net_income']
        except KeyError:
            s[account_type]['accounts'][account_name]['items'].update({'net_income':{0:0}})

        # fill preceding NI fields with 0s
        for x in range(1,current_col):
            s[account_type]['accounts'][account_name]['items']['net_income'][x] = 0

        if account_type == 'debt_accounts':
            s['expenses']['sections']['Debt']['items'].update({account_name+'_Optional':{0:0}})
            # fill preceding optional debt expense fields with 0s
            for x in range(1,current_col):
                s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][x] = 0
            
            while current_col < 121:
                s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = 0 #initialize to 0
                s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][current_col] = 0
                s = calculate_totals_for_x(s, current_col)

                if carryover_NI > 0:
                    this_col_NI = carryover_NI
                    carryover_NI = 0
                else:
                    this_col_NI = s['net_income'][current_col]
                
                total_due = s[account_type]['accounts'][account_name]['items']['beginning_balance'][current_col] + s[account_type]['accounts'][account_name]['items']['interest'][current_col] + s[account_type]['accounts'][account_name]['items']['payments'][current_col]
                #print current_col, ' ',total_due, s[account_type]['accounts'][account_name]['items']['beginning_balance'][current_col]
                if this_col_NI <= total_due:
                    s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = (-1) * this_col_NI
                    s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][current_col] = this_col_NI
                else:
                    s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = (-1) * total_due
                    s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][current_col] = total_due
                    carryover_NI = this_col_NI - total_due
                    break
                s = calculate_totals_for_x(s, current_col)
                #print 'beg bal: ',s[account_type]['accounts'][account_name]['items']['beginning_balance'][current_col]
                current_col += 1
                #s = calculate_totals_for_x(s, current_col)
                
            # fill remaining NI and debt expensefields with 0s
            for x in range(current_col + 1,121):
                s[account_type]['accounts'][account_name]['items']['net_income'][x] = 0
                s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][x] = 0
        elif account_type == 'cash_accounts':
            max_balance = item['max_balance']
            while current_col < 121:
                s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = 0 #initialize to 0
                s = calculate_totals_for_x(s, current_col)

                if carryover_NI > 0:
                    this_col_NI = carryover_NI
                    carryover_NI = 0
                else:
                    this_col_NI = s['net_income'][current_col]

                if max_balance:
                    current_balance = s[account_type]['accounts'][account_name]['items']['beginning_balance'][current_col]
                    if current_balance < max_balance: 
                        if (current_balance + this_col_NI) < max_balance:
                            s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = this_col_NI
                        else:
                            amount_needed = max_balance - current_balance
                            s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = amount_needed
                            carryover_NI = this_col_NI - amount_needed
                            break
                    else:
                        raise Exception('current_balance (%s) > max_balance (%s)' % current_balance,max_balance)
                else:
                    s[account_type]['accounts'][account_name]['items']['net_income'][current_col] = this_col_NI
                s = calculate_totals_for_x(s, current_col)
                current_col += 1
                #s = calculate_totals_for_x(s, current_col)
            # fill remaining NI fields with 0s
            for x in range(current_col + 1,121):
                s[account_type]['accounts'][account_name]['items']['net_income'][x] = 0
        else:
            raise Exception('Invalid account type: %s' % account_type)
    
    return s
"""

def allocate_NI_2(q):
    s = q
    #NI_order = [{'type':'debt_accounts','name':'Credit Card'},{'type':'debt_accounts','name':'Student'},{'type':'cash_accounts','name':'Investment','max_balance':False}]

    #pay down debt accounts, highest rate first, then contribute to "Investment" account
    debt_accounts_sorted = []
    for account in s['debt_accounts']['accounts']:
        if s['debt_accounts']['accounts'][account]['items']['ending_balance'][0] > 0:
            debt_accounts_sorted.append({'type':'debt_accounts','name':account,'rate':s['debt_accounts']['accounts'][account]['rate']})
    from operator import itemgetter
    debt_accounts_sorted = sorted(debt_accounts_sorted, key=itemgetter('rate'), reverse=True) #sort by highest rate
    for item,d in enumerate(debt_accounts_sorted):
        del debt_accounts_sorted[item]['rate']
    NI_order = debt_accounts_sorted
    NI_order.append({'type':'cash_accounts','name':'Investment','max_balance':False})

    s['cash_accounts']['accounts']['Checking']['items'].update({'net_income':{0:0}})
    s.update({'NI_allocation':[]})
    for item in NI_order:
        account_type = item['type']
        account_name = item['name']
        s[account_type]['accounts'][account_name]['items'].update({'net_income':{0:0}})
        if account_type == 'debt_accounts':
            s['expenses']['sections']['Debt']['items'].update({account_name+'_Optional':{0:0}})
        
        for x in range(0,global_max_months):
            s['cash_accounts']['accounts']['Checking']['items']['net_income'][x] = 0
            s[account_type]['accounts'][account_name]['items']['net_income'][x] = 0
            if account_type == 'debt_accounts':
                s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][x] = 0
    
    for x in range(1,global_max_months):
        s = calculate_totals_for_x(s, x)

        if s['net_income'][x] < 0:
            s['cash_accounts']['accounts']['Checking']['items']['net_income'][x] = s['net_income'][x]
        else:
            carryover_NI = 0
            for item in NI_order:
                account_type = item['type']
                account_name = item['name']

                if carryover_NI > 0:
                    this_col_NI = carryover_NI
                    carryover_NI = 0
                else:
                    this_col_NI = s['net_income'][x]

                if account_type == 'debt_accounts':
                    if s[account_type]['accounts'][account_name]['items']['ending_balance'][x] == 0:
                        continue
                    else:
                        #allocate. if partial alloc, create overflow, reduce x, reloop
                        total_due = s[account_type]['accounts'][account_name]['items']['beginning_balance'][x] + s[account_type]['accounts'][account_name]['items']['interest'][x] + s[account_type]['accounts'][account_name]['items']['payments'][x]
                        #print current_col, ' ',total_due, s[account_type]['accounts'][account_name]['items']['beginning_balance'][current_col]
                        if this_col_NI <= total_due:
                            s[account_type]['accounts'][account_name]['items']['net_income'][x] = (-1) * this_col_NI
                            s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][x] = this_col_NI
                            break
                        else:
                            s[account_type]['accounts'][account_name]['items']['net_income'][x] = (-1) * total_due
                            s['expenses']['sections']['Debt']['items'][account_name+'_Optional'][x] = total_due
                            carryover_NI = this_col_NI - total_due

                elif account_type == 'cash_accounts':
                    max_balance = item['max_balance']
                    if max_balance:
                        current_balance = s[account_type]['accounts'][account_name]['items']['beginning_balance'][x]
                        if current_balance < max_balance: 
                            if (current_balance + this_col_NI) < max_balance:
                                s[account_type]['accounts'][account_name]['items']['net_income'][x] = this_col_NI
                                break
                            else:
                                amount_needed = max_balance - current_balance
                                s[account_type]['accounts'][account_name]['items']['net_income'][x] = amount_needed
                                carryover_NI = this_col_NI - amount_needed
                        else:
                            raise Exception('current_balance (%s) > max_balance (%s)' % current_balance,max_balance)
                    else:
                        s[account_type]['accounts'][account_name]['items']['net_income'][x] = this_col_NI
                        break
                else:
                    raise Exception('Invalid account type: %s' % account_type)
        s = calculate_totals_for_x(s, x)
    #s = calc_NI_allocation_changes(s)
    return s, NI_order

def NI_allocation_introspection(s, NI_order):
    for item in NI_order:
        account_type = item['type']
        account_name = item['name']
        if account_type == 'debt_accounts':
            s['NI_allocation'].append({'type':'debt_accounts','name':account_name,'minimum_payment':-1*s[account_type]['accounts'][account_name]['items']['payments'][1],'extra_payment':0,'total_payment':0,'start_date':0,'payoff_date':0})
            for x in range(1,global_max_months):
                if s[account_type]['accounts'][account_name]['items']['net_income'][x] == 0:
                    continue
                else:
                    if (-1*s[account_type]['accounts'][account_name]['items']['net_income'][x]) < (-1*s[account_type]['accounts'][account_name]['items']['net_income'][x+1]):
                        #idea is to skip forward one month to capture the full size of the contribution in case we land on a partial allocation
                        s['NI_allocation'][-1]['start_date'] = x + 1
                        s['NI_allocation'][-1]['extra_payment'] = -1*s[account_type]['accounts'][account_name]['items']['net_income'][x+1]
                        break
                    else:
                        s['NI_allocation'][-1]['start_date'] = x
                        s['NI_allocation'][-1]['extra_payment'] = -1*s[account_type]['accounts'][account_name]['items']['net_income'][x]
                        break
            s['NI_allocation'][-1]['total_payment'] = s['NI_allocation'][-1]['minimum_payment'] + s['NI_allocation'][-1]['extra_payment']
            start_date_found = False
            for x in range(1,global_max_months):
                if (-1*s[account_type]['accounts'][account_name]['items']['net_income'][x]) < 1: #instead of "== 0" for imprecision. Also, "net_income" has a negative sign if it was allocated, since it deducts from the balance, so I'm switching it to positive here for clarity
                    if start_date_found:
                        s['NI_allocation'][-1]['payoff_date'] = x-1
                        break
                else:
                    start_date_found = True
        else:
            s['NI_allocation'].append({'type':'cash_accounts','name':account_name,'contribution':0,'start_date':0,'end_balance':0})
            for x in range(1,global_max_months):
                if s[account_type]['accounts'][account_name]['items']['net_income'][x] < 1: #instead of "== 0" for imprecision. "net_income" has a positive sign here
                    continue
                else:
                    if s[account_type]['accounts'][account_name]['items']['net_income'][x] < s[account_type]['accounts'][account_name]['items']['net_income'][x+1]:
                        #idea is to skip forward one month to capture the full size of the contribution in case we land on a partial allocation
                        s['NI_allocation'][-1]['start_date'] = x + 1
                        s['NI_allocation'][-1]['contribution'] = s[account_type]['accounts'][account_name]['items']['net_income'][x+1]
                        break
                    else:
                        s['NI_allocation'][-1]['start_date'] = x
                        s['NI_allocation'][-1]['contribution'] = s[account_type]['accounts'][account_name]['items']['net_income'][x]
                        break
            s['NI_allocation'][-1]['end_balance'] = s[account_type]['accounts'][account_name]['items']['ending_balance'][120]
    print s['NI_allocation']
    return s

def calculate_totals(s):
    # income section #
    for x in range(0,global_max_months):
        s['income']['total'][x] = 0
        for k in s['income']['items']:
            s['income']['total'][x] += s['income']['items'][k][x]


    # expense section #
    for name in s['expenses']['sections']:
        for x in range(0,global_max_months):
            s['expenses']['sections'][name]['total'][x] = 0
            for k in s['expenses']['sections'][name]['items']:
                s['expenses']['sections'][name]['total'][x] += s['expenses']['sections'][name]['items'][k][x]

    for x in range(0,global_max_months):
        s['expenses']['total'][x] = 0
        for section in s['expenses']['sections']:
            s['expenses']['total'][x] += s['expenses']['sections'][section]['total'][x]

    # net income #
    for x in range(0,global_max_months):
        s['net_income'][x] = s['income']['total'][x] - s['expenses']['total'][x]


    # assets section #
    for x in range (0,global_max_months):
        s['cash_accounts']['total'][x] = 0
        for k,v in s['cash_accounts']['accounts'].iteritems():
            s['cash_accounts']['total'][x] += s['cash_accounts']['accounts'][k]['items']['ending_balance'][x]

    """
    ## net income allocation ##
    target_name = 'Checking'
    for x in range (1,global_max_months):
        s['cash_accounts']['accounts'][target_name]['items']['net_income'][x] = s['net_income'][x]
        s['cash_accounts']['accounts'][target_name]['items']['ending_balance'][x] = s['cash_accounts']['accounts'][target_name]['items']['beginning_balance'][x] - s['cash_accounts']['accounts'][target_name]['items']['withdrawal'][x] + s['cash_accounts']['accounts'][target_name]['items']['interest'][x] + s['cash_accounts']['accounts'][target_name]['items']['net_income'][x]
    """

    # debt section #

    for x in range (0,global_max_months):
        s['debt_accounts']['total_debt'][x] = 0
        for k,v in s['debt_accounts']['accounts'].iteritems():
            s['debt_accounts']['total_debt'][x] += s['debt_accounts']['accounts'][k]['items']['ending_balance'][x]

    for x in range(0,global_max_months):
        s['debt_accounts']['debt_expense_summary']['interest_paid'][x] = 0
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['interest_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x]

    for x in range(0,global_max_months):
        s['debt_accounts']['debt_expense_summary']['principal_paid'][x] = 0
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['principal_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x]
        s['debt_accounts']['debt_expense_summary']['principal_paid'][x] = -(s['debt_accounts']['debt_expense_summary']['principal_paid'][x])

    for x in range(0,global_max_months):
        s['debt_accounts']['debt_expense_summary']['total_expense'][x] = s['debt_accounts']['debt_expense_summary']['interest_paid'][x] + s['debt_accounts']['debt_expense_summary']['principal_paid'][x]

    # net worth calc #
    for x in range (0,global_max_months):
        s['net_worth'][x] = s['cash_accounts']['total'][x] - s['debt_accounts']['total_debt'][x]

    return s


def calculate_totals_for_x(s, x):
    # assets section #
    s['cash_accounts']['total'][x] = 0
    for k,v in s['cash_accounts']['accounts'].iteritems():
        s['cash_accounts']['accounts'][k]['items']['ending_balance'][x] = 0 #reset to 0 to resum
        rate = s['cash_accounts']['accounts'][k]['rate']

        prev_ending_balance = s['cash_accounts']['accounts'][k]['items']['ending_balance'][x-1]
        s['cash_accounts']['accounts'][k]['items']['beginning_balance'][x] = prev_ending_balance
        s['cash_accounts']['accounts'][k]['items']['withdrawal'][x] = 0
        s['cash_accounts']['accounts'][k]['items']['interest'][x] = prev_ending_balance * (rate/12.0)
        for k2,v2 in s['cash_accounts']['accounts'][k]['items'].iteritems():
            if k2 == 'ending_balance':
                continue
            else:
                s['cash_accounts']['accounts'][k]['items']['ending_balance'][x] += v2[x]
        s['cash_accounts']['total'][x] += s['cash_accounts']['accounts'][k]['items']['ending_balance'][x]


    # debt section #
    s['debt_accounts']['total_debt'][x] = 0
    for k,v in s['debt_accounts']['accounts'].iteritems():
        s['debt_accounts']['accounts'][k]['items']['ending_balance'][x] = 0 #reset to 0 to re-sum
        rate = s['debt_accounts']['accounts'][k]['rate']

        prev_ending_balance = s['debt_accounts']['accounts'][k]['items']['ending_balance'][x-1]
        s['debt_accounts']['accounts'][k]['items']['beginning_balance'][x] = prev_ending_balance
        interest_expense = prev_ending_balance * (rate/12.0)
        s['debt_accounts']['accounts'][k]['items']['interest'][x] = interest_expense
        debt_expense_period_x = s['expenses']['sections']['Debt']['items'][k][0] #ie input value = min pmnt
        remaining_due = prev_ending_balance + interest_expense
        if debt_expense_period_x >= remaining_due:
            s['debt_accounts']['accounts'][k]['items']['payments'][x] = (-1) * remaining_due
            s['expenses']['sections']['Debt']['items'][k][x] = remaining_due
            """
            #recalc debt expense total (since it was already calced above, but now we're changing the expenses around)
            s['expenses']['sections']['Debt']['total'][x] = 0
            for k2 in s['expenses']['sections']['Debt']['items']:
                s['expenses']['sections']['Debt']['total'][x] += s['expenses']['sections']['Debt']['items'][k2][x]
            s['expenses']['total'][x] = 0
            for section in s['expenses']['sections']:
                    s['expenses']['total'][x] += s['expenses']['sections'][section]['total'][x]
            """
        else:
            s['debt_accounts']['accounts'][k]['items']['payments'][x] = (-1) * debt_expense_period_x
            s['expenses']['sections']['Debt']['items'][k][x] = debt_expense_period_x

        for k2,v2 in s['debt_accounts']['accounts'][k]['items'].iteritems():
            if k2 == 'ending_balance':
                continue
            else:
                s['debt_accounts']['accounts'][k]['items']['ending_balance'][x] += v2[x]
        s['debt_accounts']['total_debt'][x] += s['debt_accounts']['accounts'][k]['items']['ending_balance'][x]

    s['debt_accounts']['debt_expense_summary']['interest_paid'][x] = 0
    for name in s['debt_accounts']['accounts']:
        s['debt_accounts']['debt_expense_summary']['interest_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x]

    s['debt_accounts']['debt_expense_summary']['principal_paid'][x] = 0
    for name in s['debt_accounts']['accounts']:
        s['debt_accounts']['debt_expense_summary']['principal_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x]
        try:
            s['debt_accounts']['debt_expense_summary']['principal_paid'][x] -= s['expenses']['sections']['Debt']['items'][name+'_Optional'][x]
        except KeyError:
            pass
    s['debt_accounts']['debt_expense_summary']['principal_paid'][x] = -(s['debt_accounts']['debt_expense_summary']['principal_paid'][x])

    s['debt_accounts']['debt_expense_summary']['total_expense'][x] = s['debt_accounts']['debt_expense_summary']['interest_paid'][x] + s['debt_accounts']['debt_expense_summary']['principal_paid'][x]


    # net worth calc #
    s['net_worth'][x] = s['cash_accounts']['total'][x] - s['debt_accounts']['total_debt'][x]


    # income section #
    s['income']['total'][x] = 0
    for k in s['income']['items']:
        s['income']['total'][x] += s['income']['items'][k][x]

    # expense section #
    for name in s['expenses']['sections']:    
        s['expenses']['sections'][name]['total'][x] = 0
        for k in s['expenses']['sections'][name]['items']:
            s['expenses']['sections'][name]['total'][x] += s['expenses']['sections'][name]['items'][k][x]

    s['expenses']['total'][x] = 0
    for section in s['expenses']['sections']:
            s['expenses']['total'][x] += s['expenses']['sections'][section]['total'][x]

    # net income #
    s['net_income'][x] = s['income']['total'][x] - s['expenses']['total'][x]
    #print 'NI: ',s['net_income'][x]


    return s


def build_income_section(s, income):
    s.update({'income': {'items': {}, 'total': {}}})
    for k,v in income.iteritems():
        s['income']['items'].update({k:{}})

        input_type = v['type']
        if input_type == 'flatline':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_flatline_vector(s, 'income', k, v['frequency'], value)
        elif input_type == 'pct_change':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_pct_change_vector(s, 'income', k, v['frequency'], value, float(v['change']), v['change_frequency'], v['change_direction'], float(v['change_periods']))
        elif input_type == 'val_change':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_val_change_vector(s, 'income', k, v['frequency'], value, float(v['change']), v['change_frequency'], v['change_direction'], float(v['change_periods']))
        elif input_type == 'custom':
            s = populate_custom_vector(s, 'income', k, v['data'])

    for x in range(0,global_max_months):
        s['income']['total'].update({x:0})
        for k in s['income']['items']:
            s['income']['total'][x] += s['income']['items'][k][x]
    return s

def populate_flatline_vector(s, section, item_name, frequency, value):
    if frequency == 'yearly':
        monthly_value = value / 12.0
    elif frequency == 'monthly':
        monthly_value = value
    elif frequency == 'weekly':
        monthly_value = value * (52.0/12.0)
    
    if section == 'income':
        for x in range(0,global_max_months):
            s[section]['items'][item_name][x] = monthly_value
    elif section == 'Basic' or section == 'Misc' or section == 'Debt':
        for x in range(0,global_max_months):
            s['expenses']['sections'][section]['items'][item_name][x] = monthly_value
    return s

def populate_pct_change_vector(s, section, item_name, frequency, value, change, change_frequency, change_direction, change_periods):
    monthly_value = 0
    if frequency == 'yearly':
        monthly_value = value / 12.0
    elif frequency == 'monthly':
        monthly_value = value
    elif frequency == 'weekly':
        monthly_value = value * (52.0/12.0)
    
    change_pct = change / 100.0
    if change_direction == 'decreases':
        change_pct = change_pct * (-1)

    if section == 'income':
        s[section]['items'][item_name][0] = monthly_value
        for x in range(1,global_max_months):
            if ((change_frequency == 'year') and (x % (12 * change_periods) == 0)) or ((change_frequency == 'month') and (x % change_periods)==0):
                monthly_value = monthly_value * (1 + change_pct)
            s[section]['items'][item_name][x] = monthly_value
    elif section == 'Basic' or section == 'Misc' or section == 'Debt':
        s['expenses']['sections'][section]['items'][item_name][0] = monthly_value
        for x in range(1,global_max_months):
            if ((change_frequency == 'year') and (x % (12 * change_periods) == 0)) or ((change_frequency == 'month') and (x % change_periods == 0)):
                monthly_value = monthly_value * (1 + change_pct)
            s['expenses']['sections'][section]['items'][item_name][x] = monthly_value
    return s

def populate_val_change_vector(s, section, item_name, frequency, value, change, change_frequency, change_direction, change_periods):
    monthly_value = 0
    if frequency == 'yearly':
        monthly_value = value / 12.0
    elif frequency == 'monthly':
        monthly_value = value
    elif frequency == 'weekly':
        monthly_value = value * (52.0/12.0)
    
    change_val = change
    if change_direction == 'decreases':
        change_val = change_val * (-1)

    if section == 'income':
        s[section]['items'][item_name][0] = monthly_value
        for x in range(1,global_max_months):
            if ((change_frequency == 'year') and (x % (12 * change_periods) == 0)) or ((change_frequency == 'month') and (x % change_periods)):
                monthly_value = monthly_value + change_val
                if monthly_value < 0:
                    monthly_value = 0
            s[section]['items'][item_name][x] = monthly_value
    elif section == 'Basic' or section == 'Misc' or section == 'Debt':
        s['expenses']['sections'][section]['items'][item_name][0] = monthly_value
        for x in range(1,global_max_months):
            if ((change_frequency == 'year') and (x % (12 * change_periods) == 0)) or ((change_frequency == 'month') and (x % change_periods == 0)):
                monthly_value = monthly_value + change_val
                if monthly_value < 0:
                    monthly_value = 0
            s['expenses']['sections'][section]['items'][item_name][x] = monthly_value
    return s

def populate_custom_vector(s, section, item_name, data):
    actual_start_mo = 7
    actual_start_yr = 2013
    actual_end_mo = actual_start_mo - 1
    actual_end_yr = actual_start_yr + 10

    #set whole vector to 0 first, then fill in data as per the given data
    if section == 'income':
        for x in range(0,global_max_months):
            s[section]['items'][item_name][x] = 0
    elif section == 'Basic' or section == 'Misc' or section == 'Debt':
        for x in range(0,global_max_months):
            s['expenses']['sections'][section]['items'][item_name][x] = 0

    for period in data:
        try:
            value = float(period['value'])
        except:
            value = 0.0
        if value < 0:
            value = 0
        
        frequency = period['frequency']
        if frequency == 'yearly':
            monthly_value = value / 12.0
        elif frequency == 'monthly':
            monthly_value = value
        elif frequency == 'weekly':
            monthly_value = value * (52.0/12.0)

        start_mo = int(period['start_mo'])
        start_yr = int(period['start_yr'])
        if start_yr == actual_start_yr and start_mo < actual_start_mo:
            start_mo = actual_start_mo
        end_mo = int(period['end_mo'])
        end_yr = int(period['end_yr'])
        if end_yr > actual_end_yr:
            end_yr = actual_end_yr
        if end_yr == actual_end_yr and end_mo > actual_end_mo:
            end_mo = actual_end_mo

        start_month_number = (start_mo - actual_start_mo + 1) + ( (start_yr - actual_start_yr) * 12 )
        end_month_number = (end_mo - actual_start_mo + 1) + ( (end_yr - actual_start_yr) * 12 )
        if start_month_number > 120 or start_month_number < 1 or end_month_number > 120 or end_month_number < 1 or start_month_number > end_month_number:
            raise Exception("custom input error. start_mo = %s; start_yr = %s; end_mo = %s; end_yr = %s; start_month_number = %s; end_month_number = %s" % (start_mo,start_yr, end_mo, end_yr,start_month_number, end_month_number))

        for x in range(start_month_number,end_month_number+1):
            if section == 'income':
                s[section]['items'][item_name][x] = monthly_value         
            elif section == 'Basic' or section == 'Misc' or section == 'Debt':
                s['expenses']['sections'][section]['items'][item_name][x] = monthly_value
    return s


def build_expense_section(s, basic_expenses, debt_expenses, misc_expenses):
    s.update({'expenses':{'sections':{},'total':{}}})
    s = build_expense_subsection(s, basic_expenses, 'Basic')
    s = build_expense_subsection(s, debt_expenses, 'Debt')
    s = build_expense_subsection(s, misc_expenses, 'Misc')
    s = sum_expenses(s)
    return s


def build_expense_subsection(s, expense_dict, name):
    s['expenses']['sections'].update({name:{'items':{},'total':{}}})
    for k,v in expense_dict.iteritems():
        s['expenses']['sections'][name]['items'].update({ k:{} })

        input_type = v['type']
        if input_type == 'flatline':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_flatline_vector(s, name, k, v['frequency'], value)
        elif input_type == 'pct_change':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_pct_change_vector(s, name, k, v['frequency'], value, float(v['change']), v['change_frequency'], v['change_direction'], float(v['change_periods']))
        elif input_type == 'val_change':
            try:
                value = float(v['value'])
            except:
                value = 0.0
            s = populate_val_change_vector(s, name, k, v['frequency'], value, float(v['change']), v['change_frequency'], v['change_direction'], float(v['change_periods']))
        elif input_type == 'custom':
            s = populate_custom_vector(s, name, k, v['data'])

    for x in range(0,global_max_months):
        s['expenses']['sections'][name]['total'].update({x:0})
        for k in s['expenses']['sections'][name]['items']:
            s['expenses']['sections'][name]['total'][x] += s['expenses']['sections'][name]['items'][k][x]

    return s

def sum_expenses(s):
    for x in range(0,global_max_months):
        s['expenses']['total'].update({x:0})
        for section in s['expenses']['sections']:
            s['expenses']['total'][x] += s['expenses']['sections'][section]['total'][x]

    return s
    
def calculate_net_income(s):
    s.update({'net_income':{}})
    for x in range(0,global_max_months):
        net_income = s['income']['total'][x] - s['expenses']['total'][x]
        s['net_income'].update({x:net_income})

    return s

def build_cash_section(s, cash_accounts):
    s['cash_accounts'] = {'accounts':{},'total':{}}
    #print cash_balances
    for name,data in cash_accounts.iteritems():
        #name = k[:-8]
        s['cash_accounts']['accounts'].update({name:{'rate':float(data['rate'])/100.0,'items': {'beginning_balance':{},'withdrawal':{},'interest':{},'ending_balance':{0:float(data['balance'])} } } } )
        s = build_cash_sub_section(s, name)

    s = build_cash_summary(s)

    return s

def build_cash_sub_section(s, name):
    rate = s['cash_accounts']['accounts'][name]['rate']
    
    s['cash_accounts']['accounts'][name]['items']['beginning_balance'][0] = 0
    s['cash_accounts']['accounts'][name]['items']['withdrawal'][0] = 0
    s['cash_accounts']['accounts'][name]['items']['interest'][0] = 0

    for x in range(1,global_max_months):
        prev_ending_balance = s['cash_accounts']['accounts'][name]['items']['ending_balance'][x-1]
        s['cash_accounts']['accounts'][name]['items']['beginning_balance'][x] = prev_ending_balance
        s['cash_accounts']['accounts'][name]['items']['withdrawal'][x] = 0
        s['cash_accounts']['accounts'][name]['items']['interest'][x] = prev_ending_balance * (rate/12.0)

        s['cash_accounts']['accounts'][name]['items']['ending_balance'][x] = s['cash_accounts']['accounts'][name]['items']['beginning_balance'][x] - s['cash_accounts']['accounts'][name]['items']['withdrawal'][x] + s['cash_accounts']['accounts'][name]['items']['interest'][x]
    return s

def build_cash_summary(s):
    for x in range (0,global_max_months):
        s['cash_accounts']['total'].update({x:0})
        for k,v in s['cash_accounts']['accounts'].iteritems():
            s['cash_accounts']['total'][x] += s['cash_accounts']['accounts'][k]['items']['ending_balance'][x]

    return s

def build_debt_section(s, debt_accounts):
    s['debt_accounts'] = {'accounts':{},'total_debt':{},'debt_expense_summary':{},'debt_expense_summary_min':{}}
    #for k,balance in debt_balances.iteritems():
    for name,data in debt_accounts.iteritems():
        #name = k[:-8]
        s['debt_accounts']['accounts'].update({name:{'rate':float(data['rate'])/100.0,'items': {'beginning_balance':{},'payments':{},'interest':{},'ending_balance':{0:float(data['balance'])} } } } )
        
        s = build_debt_sub_section(s, name)

    #s,iterations = build_debt_summary(s)

    #calculate totals, but don't want to call 'build_debt_summary' because it does a lot of other shit now, so just copied in these parts
    s['debt_accounts']['debt_expense_summary'].update({'interest_paid':{},'principal_paid':{},'total_expense':{}})
    for x in range (0,global_max_months):
        s['debt_accounts']['total_debt'].update({x:0})
        for k,v in s['debt_accounts']['accounts'].iteritems():
            s['debt_accounts']['total_debt'][x] += s['debt_accounts']['accounts'][k]['items']['ending_balance'][x]

    for x in range(1,global_max_months):
        s['debt_accounts']['debt_expense_summary']['interest_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['interest_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x]

    for x in range(1,global_max_months):
        s['debt_accounts']['debt_expense_summary']['principal_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts']['debt_expense_summary']['principal_paid'][x] += (s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] - s['debt_accounts']['accounts'][name]['items']['ending_balance'][x])

    for x in range(1,global_max_months):
        s['debt_accounts']['debt_expense_summary']['total_expense'].update({x:0})
        s['debt_accounts']['debt_expense_summary']['total_expense'][x] = s['debt_accounts']['debt_expense_summary']['interest_paid'][x] + s['debt_accounts']['debt_expense_summary']['principal_paid'][x]

    return s

def build_debt_sub_section(s, name):
    rate = s['debt_accounts']['accounts'][name]['rate']
    s['debt_accounts']['accounts'][name]['items']['beginning_balance'][0] = 0
    s['debt_accounts']['accounts'][name]['items']['payments'][0] = 0
    s['debt_accounts']['accounts'][name]['items']['interest'][0] = 0
    for x in range(1,global_max_months):
        prev_ending_balance = s['debt_accounts']['accounts'][name]['items']['ending_balance'][x-1]
        s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] = prev_ending_balance
        interest_expense = prev_ending_balance * (rate/12.0)
        s['debt_accounts']['accounts'][name]['items']['interest'][x] = interest_expense
        debt_expense_period_x = s['expenses']['sections']['Debt']['items'][name][x]
        remaining_due = prev_ending_balance + interest_expense
        if debt_expense_period_x >= remaining_due:
            s['debt_accounts']['accounts'][name]['items']['payments'][x] = (-1) * remaining_due
            s['expenses']['sections']['Debt']['items'][name][x] = remaining_due
        else:
            s['debt_accounts']['accounts'][name]['items']['payments'][x] = (-1) * debt_expense_period_x
        
        s['debt_accounts']['accounts'][name]['items']['ending_balance'][x] = s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x] + s['debt_accounts']['accounts'][name]['items']['interest'][x]

    return s

def build_debt_summary(s, min_payment=False, iterations=global_max_months):
    #have thsi min_payment switch so when I run this the first time, before net income is allocated, it'll save that earlier version for use in comparison
    if min_payment:
        debt_expense_summary = 'debt_expense_summary_min'
    else:
        debt_expense_summary = 'debt_expense_summary'

    for account in s['debt_accounts']['accounts']:
        try:
            payoff_date = s['debt_accounts']['accounts'][account][debt_expense_summary]['payoff_date']
        except KeyError:
            payoff_date = 0
        
        s['debt_accounts']['accounts'][account].update({debt_expense_summary:{'total_interest_paid':0,'total_principal_paid':0,'total_debt_expense':0,'payoff_date':payoff_date}})

        for x in range (1,iterations):
            if s['debt_accounts']['accounts'][account]['items']['ending_balance'][x] < 1: #wont ever be true on the recall because it stops one short of getting to zero
                s['debt_accounts']['accounts'][account][debt_expense_summary]['payoff_date'] = x
                break
        if s['debt_accounts']['accounts'][account][debt_expense_summary]['payoff_date'] == 0: #ie not paid off in 10 years
            #project it out until it's paid off, recall this whole function with the new number of iterations, and once that finishes just return s so the rest of this doesn't run again
            s = project_debt_further(s, account, debt_expense_summary, min_payment)
            #print 'YES', account
            return s, s['debt_accounts']['accounts'][account][debt_expense_summary]['payoff_date']

        for x in range(1,iterations):
            s['debt_accounts']['accounts'][account][debt_expense_summary]['total_interest_paid'] += s['debt_accounts']['accounts'][account]['items']['interest'][x]
            s['debt_accounts']['accounts'][account][debt_expense_summary]['total_principal_paid'] += (s['debt_accounts']['accounts'][account]['items']['beginning_balance'][x] - s['debt_accounts']['accounts'][account]['items']['ending_balance'][x])
            #print s['debt_accounts']['accounts'][account][debt_expense_summary]['total_principal_paid']
            s['debt_accounts']['accounts'][account][debt_expense_summary]['total_debt_expense'] += s['debt_accounts']['accounts'][account]['items']['interest'][x] + ((s['debt_accounts']['accounts'][account]['items']['beginning_balance'][x] - s['debt_accounts']['accounts'][account]['items']['ending_balance'][x]))
        print account, payoff_date, debt_expense_summary
    #below is in aggregate
    s['debt_accounts'][debt_expense_summary].update({'interest_paid':{},'total_interest_paid':0,'principal_paid':{},'total_principal_paid':0,'total_expense':{},'total_debt_expense':0,'payoff_date':0})
    for x in range (0,iterations):
        s['debt_accounts']['total_debt'].update({x:0})
        for k,v in s['debt_accounts']['accounts'].iteritems():
            s['debt_accounts']['total_debt'][x] += s['debt_accounts']['accounts'][k]['items']['ending_balance'][x]

    for account in s['debt_accounts']['accounts']:
        s['debt_accounts'][debt_expense_summary]['payoff_date'] = max(s['debt_accounts'][debt_expense_summary]['payoff_date'],s['debt_accounts']['accounts'][account][debt_expense_summary]['payoff_date'])

    for x in range(1,iterations):
        s['debt_accounts'][debt_expense_summary]['interest_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            s['debt_accounts'][debt_expense_summary]['interest_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x]
            s['debt_accounts'][debt_expense_summary]['total_interest_paid'] += s['debt_accounts']['accounts'][name]['items']['interest'][x]

    for x in range(1,iterations):
        s['debt_accounts'][debt_expense_summary]['principal_paid'].update({x:0})
        for name in s['debt_accounts']['accounts']:
            #s['debt_accounts'][debt_expense_summary]['principal_paid'][x] += s['debt_accounts']['accounts'][name]['items']['interest'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x] 
            s['debt_accounts'][debt_expense_summary]['principal_paid'][x] += (s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] - s['debt_accounts']['accounts'][name]['items']['ending_balance'][x])
        #s['debt_accounts'][debt_expense_summary]['principal_paid'][x] = -(s['debt_accounts'][debt_expense_summary]['principal_paid'][x])
        s['debt_accounts'][debt_expense_summary]['total_principal_paid'] += s['debt_accounts'][debt_expense_summary]['principal_paid'][x]

    for x in range(1,iterations):
        s['debt_accounts'][debt_expense_summary]['total_expense'].update({x:0})
        s['debt_accounts'][debt_expense_summary]['total_expense'][x] = s['debt_accounts'][debt_expense_summary]['interest_paid'][x] + s['debt_accounts'][debt_expense_summary]['principal_paid'][x]
        s['debt_accounts'][debt_expense_summary]['total_debt_expense'] += s['debt_accounts'][debt_expense_summary]['total_expense'][x]

    no_debt = True
    for x in range(0,iterations):
        if s['debt_accounts']['total_debt'][x] > 0:
            no_debt = False
            break
    s['debt_accounts'].update({'no_debt':no_debt})

    return s, iterations

def project_debt_further(s, name, debt_expense_summary, min_payment): # name = debt account name
    rate = s['debt_accounts']['accounts'][name]['rate']
    x = 121
    
    debt_expense_period_x = s['expenses']['sections']['Debt']['items'][name][120] + (s['net_income_raw'][120] if s['net_income_raw'][120] > 0 else 0)

    while True:
        #print x
        prev_ending_balance = s['debt_accounts']['accounts'][name]['items']['ending_balance'][x-1]
        s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] = prev_ending_balance
        interest_expense = prev_ending_balance * (rate/12.0)
        s['debt_accounts']['accounts'][name]['items']['interest'][x] = interest_expense
        
        remaining_due = prev_ending_balance + interest_expense
        if debt_expense_period_x >= remaining_due:
            s['debt_accounts']['accounts'][name]['items']['payments'][x] = (-1) * remaining_due
            #s['expenses']['sections']['Debt']['items'][name][x] = remaining_due
        else:
            s['debt_accounts']['accounts'][name]['items']['payments'][x] = (-1) * debt_expense_period_x
        
        s['debt_accounts']['accounts'][name]['items']['ending_balance'][x] = s['debt_accounts']['accounts'][name]['items']['beginning_balance'][x] + s['debt_accounts']['accounts'][name]['items']['payments'][x] + s['debt_accounts']['accounts'][name]['items']['interest'][x]

        if s['debt_accounts']['accounts'][name]['items']['ending_balance'][x] < 1:
            s['debt_accounts']['accounts'][name][debt_expense_summary]['payoff_date'] = x
            if min_payment == False: # just so it doesn't reach this part before s['NI_allocation'] is actually created
                for idx,item in enumerate(s['NI_allocation']):
                    print item['name'], name
                    if item['name'] == name:
                        s['NI_allocation'][idx]['payoff_date'] = x
                        print 'YEP'
            break
        x += 1
      
    for account in s['debt_accounts']['accounts']:
        if name == account:
            continue      
        else:
            for y in range(121,x+1):
                s['debt_accounts']['accounts'][account]['items']['beginning_balance'][y] = 0
                s['debt_accounts']['accounts'][account]['items']['interest'][y] = 0
                s['debt_accounts']['accounts'][account]['items']['payments'][y] = 0
                s['debt_accounts']['accounts'][account]['items']['ending_balance'][y] = 0


    s,iterations = build_debt_summary(s, min_payment=min_payment, iterations=s['debt_accounts']['accounts'][name][debt_expense_summary]['payoff_date'])

    return s


def calculate_net_worth(s):
    s.update({'net_worth':{}})
    for x in range (0,global_max_months):
        s['net_worth'].update({x:0})
        s['net_worth'][x] = s['cash_accounts']['total'][x] - s['debt_accounts']['total_debt'][x]

    return s
