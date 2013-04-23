from xlrd import open_workbook
from xlwt import Workbook, easyxf, Formula
from xlwt.Utils import rowcol_to_cell
from models import User

def build_xls_file(income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates):
    wb = Workbook()
    s = wb.add_sheet('Model')

    #set col width so labels fit properly
    s.col(0).width = 800
    s.col(1).width = 6800
    
    s.write(0,0, 'Personal Financial Model',easyxf('borders: bottom thick;' 'font: bold True, height 320;'))
    for x in range(1,15):
        s.write(0,x,style=easyxf('borders: bottom thick;' 'font: bold True, height 320;'))
    
    current_row = 3

    current_row = set_date_labels(s, current_row)
    
    current_row, income_total_row = build_income_section(s, current_row, income)

    current_row, expense_total_row, debt_payments_rows = build_expense_section(s, current_row, basic_expenses, debt_expenses, misc_expenses)

    current_row, net_income_total_row = calculate_net_income(s, current_row, income_total_row, expense_total_row)

    current_row, total_cash_row = build_cash_section(s, current_row, net_income_total_row, cash_balances, rates)

    current_row, total_debt_row = build_debt_section(s, current_row, debt_payments_rows, debt_balances, rates)

    current_row = calculate_net_worth(s, current_row, total_debt_row, total_cash_row) 

    wb.save('excelexpt/tmp/xlwt_ex.xls')

    return 'ok'


def set_date_labels(s, current_row):
    s.write(current_row,2, 'Today',easyxf('borders: bottom thick;' 'font: bold True;'))
    for x in range (1,13):
        s.write(current_row,2+x, 'Mon '+str(x),easyxf('borders: bottom thick;' 'font: bold True;'))

    return current_row + 1

def build_income_section(s, current_row, income):
    item_counter = 0
    s.write(current_row,1, 'Income',easyxf('borders: bottom thick;' 'font: bold True;'))
    current_row += 1

    for k,v in income.iteritems():
        this_row = current_row + item_counter
        s.write(this_row,1, '  '+k)
        s.write(this_row,2, float(v))
        for x in range(0,12):
            s.write(this_row,3+x, Formula(rowcol_to_cell(this_row,2+x)))
        item_counter += 1

    this_row = current_row+item_counter
    income_total_row = this_row

    s.write(this_row,1, 'Total Income',easyxf('borders: top thin;' 'font: bold True;'))
    for x in range(0,13):
        s.write(this_row,2+x, Formula('sum('+rowcol_to_cell(this_row-item_counter,2+x)+':'+rowcol_to_cell(this_row-1,2+x)+')'),easyxf('borders: top thin;' 'font: bold True;'))
    
    return (current_row + item_counter + 2), income_total_row

def build_expense_section(s, current_row, basic_expenses, debt_expenses, misc_expenses):
    exp_start_row = current_row

    s.write(current_row,1, 'Expenses',easyxf('borders: bottom thick;' 'font: bold True;'))
    current_row += 2

    current_row, basic_exp_item_counter = build_expense_subsection(s, current_row, basic_expenses, 'Basic')
    current_row, debt_exp_item_counter, debt_payments_rows = build_expense_subsection(s, current_row, debt_expenses, 'Debt')
    current_row, misc_exp_item_counter = build_expense_subsection(s, current_row, misc_expenses, 'Misc')
    
    current_row, expense_total_row = sum_expenses(s, current_row, exp_start_row, basic_exp_item_counter, debt_exp_item_counter, misc_exp_item_counter)

    return current_row, expense_total_row, debt_payments_rows

def build_expense_subsection(s, current_row, expense_dict, name):
    if name == 'Debt':
        debt = True
    else:
        debt = False

    item_counter = 0
    s.write(current_row,1, name + ' Expenses',easyxf('borders: bottom thin;'))
    current_row += 1
    if debt:
        debt_payments_rows = {}
    for k,v in expense_dict.iteritems():
        this_row = current_row+item_counter
        if debt:
            debt_payments_rows[k] = this_row
        s.write(this_row,1, '  '+k)
        s.write(this_row,2, float(v))
        for x in range(0,12):
            s.write(this_row,3+x, Formula(rowcol_to_cell(this_row,2+x)))
        item_counter += 1

    this_row = current_row + item_counter
    s.write(this_row,1, 'Total '+name+' Expenses',easyxf('borders: top thin;'))
    if item_counter > 0:
        for x in range(0,13):
            s.write(this_row,2+x, Formula('sum('+rowcol_to_cell(this_row-item_counter,2+x)+':'+rowcol_to_cell(this_row-1,2+x)+')'),easyxf('borders: top thin;'))
    else:
        for x in range(0,13):
            s.write(this_row,2+x,Formula('0'),easyxf('borders: top thin;'))
    
    if debt:
        return (current_row + item_counter + 2), item_counter, debt_payments_rows
    else:
        return (current_row + item_counter + 2), item_counter

def sum_expenses(s, current_row, exp_start_row, basic_exp_item_counter, debt_exp_item_counter, misc_exp_item_counter):
    this_row = current_row
    expense_total_row = current_row

    s.write(current_row,1, 'Total Expenses',easyxf('font: bold True;'))
    total_row_1 = exp_start_row + 3 + basic_exp_item_counter
    total_row_2 = total_row_1 + 3 + debt_exp_item_counter
    total_row_3 = total_row_2 + 3 + misc_exp_item_counter   
    for x in range(0,13):
        total_formula_string = rowcol_to_cell(total_row_1,2+x) + "+" + rowcol_to_cell(total_row_2,2+x) + "+" + rowcol_to_cell(total_row_3,2+x)
        s.write(current_row,2+x,Formula(total_formula_string),easyxf('font: bold True;'))

    return (current_row + 3), expense_total_row

def calculate_net_income(s, current_row, income_total_row, expense_total_row):
    s.write(current_row,1, 'Net Income',easyxf('font: bold True;'))
    for x in range(0,13):
        s.write(current_row,2+x,Formula(rowcol_to_cell(income_total_row,2+x)+'-'+rowcol_to_cell(expense_total_row,2+x)),easyxf('font: bold True;'))

    return (current_row + 4), current_row

def build_cash_section(s, current_row, net_income_total_row, cash_balances, rates):
    s.write(current_row,1, 'Cash and Investments',easyxf('font: bold True;' 'borders: bottom thick;'))
    current_row += 2
    cash_balance_rows = {}
    this_row = current_row
    for k,v in cash_balances.iteritems():
        this_row, cash_balance_rows[k] = build_cash_sub_section(s, this_row, k[:-8], rates[k[:-8]], v, net_income_total_row)

    current_row = this_row + 2

    current_row, total_cash_row = build_cash_summary(s, current_row, cash_balance_rows)

    return current_row + 3, total_cash_row



    """
    s.write(current_row,1, 'Beginning Balance')
    for x in range (0,12):
        s.write(current_row,3+x,Formula(rowcol_to_cell(current_row+2,2+x)))

    current_row += 1
    
    s.write(current_row,1, '  Net Change')
    for x in range (0,12):
        s.write(current_row,3+x,Formula(rowcol_to_cell(net_income_total_row,3+x)))

    current_row += 1
    
    s.write(current_row,1, 'Ending Balance',easyxf('borders: top thin;'))
    s.write(current_row,2, float(balances['Cash_Balance']),easyxf('borders: top thin;'))
    for x in range (0,12):
        s.write(current_row,3+x,Formula('sum('+rowcol_to_cell(current_row-2,3+x)+':'+rowcol_to_cell(current_row-1,3+x)+')'),easyxf('borders: top thin;'))

    return current_row + 3
    """

def build_cash_sub_section(s, current_row, name, rate, balance, net_income_total_row):
    s.write(current_row,1, name,easyxf('font: bold True;' 'borders: bottom thin;'))
    s.write(current_row,2, 'Return -->',easyxf('font: bold True;'))
    s.write(current_row,3, float(rate),easyxf('font: bold True;'))
    current_row += 1

    checking_row_present = 0
    if name == 'Checking':
        checking_row_present = 1

    s.write(current_row,1, 'Beginning Balance')
    for x in range (0,12):
        s.write(current_row,3+x,Formula(rowcol_to_cell(current_row+3+checking_row_present,2+x)))

    current_row += 1
    
    if checking_row_present:
        s.write(current_row,1, '  Net Income')
        for x in range (0,12):
            s.write(current_row,3+x,Formula(rowcol_to_cell(net_income_total_row,3+x)))
        current_row += 1
        
    
    s.write(current_row,1, '  Less: Withdrawals')
    for x in range (0,12):
        #s.write(current_row,3+x,Formula('-'+rowcol_to_cell(withdrawal,3+x)))
        s.write(current_row,3+x,0)

    current_row += 1
    
    s.write(current_row,1, '  Plus: Interest')
    for x in range (0,12):
        s.write(current_row,3+x,Formula('('+rowcol_to_cell(current_row-3-checking_row_present,3)+'/12)*'+rowcol_to_cell(current_row+1,2+x)))

    current_row += 1

    s.write(current_row,1, 'Ending Balance',easyxf('borders: top thin;'))
    s.write(current_row,2, float(balance),easyxf('borders: top thin;'))
    for x in range (0,12):
        s.write(current_row,3+x,Formula('sum('+rowcol_to_cell(current_row-3-checking_row_present,3+x)+':'+rowcol_to_cell(current_row-1,3+x)+')'),easyxf('borders: top thin;'))

    return (current_row + 2), current_row

def build_cash_summary(s, current_row, cash_balance_rows):
    s.write(current_row,1, 'Total Cash/Investment Assets',easyxf('font: bold True;'))
    
    for x in range (0,13):
        cash_sum_formula_string = ''
        for k,row in cash_balance_rows.iteritems():
            cash_sum_formula_string += (rowcol_to_cell(row,2+x)+'+')
        s.write(current_row,2+x,Formula(cash_sum_formula_string[:-1]))
    """
    current_row += 2

    s.write(current_row,1, 'Cash/Investment Summary',easyxf('font: bold True;' 'borders: bottom thin;'))
    current_row += 1

    s.write(current_row,1, '  Investment Income')
    for x in range (1,13):
        interest_sum_formula_string = ''
        for k,row in cash_balance_rows.iteritems():
            interest_sum_formula_string += (rowcol_to_cell(row-1,2+x)+'+')
        s.write(current_row,2+x,Formula(interest_sum_formula_string[:-1]))

    current_row += 1

    s.write(current_row,1, '  Principal Paid')
    for x in range (1,13):
        principal_sum_formula_string = ''
        for k,row in debt_balance_rows.iteritems():
            principal_sum_formula_string += '('+rowcol_to_cell(row-2,2+x)+'+'+rowcol_to_cell(row-1,2+x)+') +'
        s.write(current_row,2+x,Formula('-('+principal_sum_formula_string[:-1]+')'))

    current_row += 1

    s.write(current_row,1, 'Total Debt Expense',easyxf('borders: top thin;'))
    s.write(current_row,2,style=easyxf('borders: top thin;'))
    for x in range (1,13):
        s.write(current_row,2+x,Formula('sum('+rowcol_to_cell(current_row-2,2+x)+':'+rowcol_to_cell(current_row-1,2+x)+')'),easyxf('borders: top thin;'))
    """
    return current_row +2, current_row

def build_debt_section(s, current_row, debt_payments_rows, debt_balances, rates):
    s.write(current_row,1, 'Debt',easyxf('font: bold True;' 'borders: bottom thick;'))
    current_row += 2
    debt_balance_rows = {}
    this_row = current_row
    for k in debt_payments_rows:
        this_row, debt_balance_rows[k] = build_debt_sub_section(s, this_row, k, rates[k], debt_payments_rows[k], debt_balances[k+'_Balance'])

    current_row = this_row +2

    current_row, total_debt_row = build_debt_summary(s, current_row, debt_balance_rows)

    return current_row + 1, total_debt_row

def build_debt_sub_section(s, current_row, name, APR, debt_payments_row, balance):
    s.write(current_row,1, name +' Debt',easyxf('font: bold True;' 'borders: bottom thin;'))
    s.write(current_row,2, '  APR -->',easyxf('font: bold True;'))
    s.write(current_row,3, float(APR),easyxf('font: bold True;'))
    current_row += 1

    s.write(current_row,1, 'Beginning Balance')
    for x in range (0,12):
        s.write(current_row,3+x,Formula(rowcol_to_cell(current_row+3,2+x)))

    current_row += 1
    
    s.write(current_row,1, '  Less: Payments')
    for x in range (0,12):
        s.write(current_row,3+x,Formula('-'+rowcol_to_cell(debt_payments_row,3+x)))

    current_row += 1
    
    s.write(current_row,1, '  Plus: Interest')
    for x in range (0,12):
        s.write(current_row,3+x,Formula('('+rowcol_to_cell(current_row-3,3)+'/12)*'+rowcol_to_cell(current_row+1,2+x)))

    current_row += 1
    
    s.write(current_row,1, 'Ending Balance',easyxf('borders: top thin;'))
    s.write(current_row,2, float(balance),easyxf('borders: top thin;'))
    for x in range (0,12):
        s.write(current_row,3+x,Formula('sum('+rowcol_to_cell(current_row-3,3+x)+':'+rowcol_to_cell(current_row-1,3+x)+')'),easyxf('borders: top thin;'))

    return (current_row + 2), current_row

def build_debt_summary(s, current_row, debt_balance_rows):
    s.write(current_row,1, 'Total Debt Outstanding',easyxf('font: bold True;'))
    
    for x in range (0,13):
        debt_sum_formula_string = ''
        for k,row in debt_balance_rows.iteritems():
            debt_sum_formula_string += (rowcol_to_cell(row,2+x)+'+')
        s.write(current_row,2+x,Formula(debt_sum_formula_string[:-1]))

    total_debt_row = current_row

    current_row += 2

    s.write(current_row,1, 'Debt Expense Summary',easyxf('font: bold True;' 'borders: bottom thin;'))
    current_row += 1

    s.write(current_row,1, '  Interest Paid')
    for x in range (1,13):
        interest_sum_formula_string = ''
        for k,row in debt_balance_rows.iteritems():
            interest_sum_formula_string += (rowcol_to_cell(row-1,2+x)+'+')
        s.write(current_row,2+x,Formula(interest_sum_formula_string[:-1]))

    current_row += 1

    s.write(current_row,1, '  Principal Paid')
    for x in range (1,13):
        principal_sum_formula_string = ''
        for k,row in debt_balance_rows.iteritems():
            principal_sum_formula_string += '('+rowcol_to_cell(row-2,2+x)+'+'+rowcol_to_cell(row-1,2+x)+') +'
        s.write(current_row,2+x,Formula('-('+principal_sum_formula_string[:-1]+')'))

    current_row += 1

    s.write(current_row,1, 'Total Debt Expense',easyxf('borders: top thin;'))
    s.write(current_row,2,style=easyxf('borders: top thin;'))
    for x in range (1,13):
        s.write(current_row,2+x,Formula('sum('+rowcol_to_cell(current_row-2,2+x)+':'+rowcol_to_cell(current_row-1,2+x)+')'),easyxf('borders: top thin;'))

    return current_row+2, total_debt_row

def calculate_net_worth(s, current_row, total_debt_row, total_cash_row):
    s.write(current_row,1, 'Net Worth',easyxf('font: bold True;'))
    for x in range (0,13):
        s.write(current_row,2+x,Formula(rowcol_to_cell(total_cash_row,2+x)+'-'+rowcol_to_cell(total_debt_row,2+x)),easyxf('font: bold True;'))

    return current_row + 2



def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        if user.check_password(password):
            return user
    return False