import os
import pandas as pd


def new_portfolio(portfolio_name, date_opened, starting_balance):
    portfolio = pd.DataFrame({'portfolio_name': [portfolio_name], 'date_opened': [date_opened], 'starting_balance': [starting_balance], 'today': [''], 'current_cash': [''], 'current_equities': [''], 'current_options': [''], 'current_value': [''], 'IRR': ['']})

    portfolio['portfolio_name'] = portfolio['portfolio_name'].astype(str)
    portfolio['date_opened'] = portfolio['date_opened'].astype(int)
    portfolio['starting_balance'] = portfolio['starting_balance'].astype(float)

    # check if portfolio exists, if not, make a directory for it
    if not os.path.isdir(portfolio_name):
        os.makedirs(portfolio_name)

    # check if file exists, if yes, add transaction to that file, if not, make it with first entry as this transaction
    file = './' + portfolio_name + '/portfolio_summary.csv'
    portfolio.to_csv(file, index=False)
