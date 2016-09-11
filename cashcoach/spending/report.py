from cashcoach.spending import messages, transactions
from cashcoach.secrets import NET, GROSS, SAVINGS_RATE

def to_num(val):
    return float(val.replace("$", "").replace(",", ""))

def get_monthly_expenses(ss):
    expenses = ss.get_sheet("Expenses")
    expenses['amount'] = expenses['My Share'].apply(to_num)

    return expenses.amount.sum()

def get_flex(monthly_gross, monthly_net, monthly_expenses, savings_rate):
    monthly_savings = monthly_gross*savings_rate
    flex = monthly_net - monthly_expenses - monthly_savings
    return flex

def create_report(ss):
    expenses = get_monthly_expenses(ss)

    # TODO: get from spreadsheet
    flex = get_flex(GROSS, NET, expenses, SAVINGS_RATE)


    df = ss.get_sheet("all-together")

    targets = transactions.get_targets(df, flex)

    msgs = messages.make_messages(targets)

    return msgs
