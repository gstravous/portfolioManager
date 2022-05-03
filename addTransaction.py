import os
import pandas as pd


def add_transaction(portfolio_name, position_id, stock, exp_month, exp_day, exp_year, put_call, strike, shares, price, trade_date):
    transaction = pd.DataFrame({'portfolio_name': [portfolio_name], 'position_id': [position_id], 'stock': [stock], 'exp_month': [exp_month], 'exp_day': [exp_day], 'exp_year': [exp_year], 'put_call': [put_call], 'strike': [strike], 'shares': [shares], 'price': [price], 'trade_date': [trade_date]})

    transaction['portfolio_name'] = transaction['portfolio_name'].astype(str)
    transaction['position_id'] = transaction['position_id'].astype(str)
    transaction['stock'] = transaction['stock'].astype(str)
    transaction['exp_month'] = transaction['exp_month'].astype(str)
    transaction['exp_day'] = transaction['exp_day'].astype(str)
    transaction['exp_year'] = transaction['exp_year'].astype(str)
    transaction['put_call'] = transaction['put_call'].astype(str)
    transaction['strike'] = transaction['strike'].astype(str)
    transaction['shares'] = transaction['shares'].astype(int)
    transaction['price'] = transaction['price'].astype(float)
    transaction['trade_date'] = transaction['trade_date'].astype(int)

    transaction['debit/credit'] = transaction['shares'] * transaction['price'] * -1
    transaction['td_option_symbol'] = transaction['stock'] + '_' + transaction['exp_month'] + transaction['exp_day'] + transaction['exp_year'] + transaction['put_call'] + transaction['strike']
    transaction['exp_date'] = transaction['exp_year'] + transaction['exp_month'] + transaction['exp_day']

    def contains_number(value):
        has_number = 'F'
        for character in value:
            if character.isdigit():
                has_number = 'T'
        return has_number

    transaction['is_option'] = contains_number(transaction['td_option_symbol'])
    transaction['security_open'] = ''

    # check if portfolio exists, if not, make a directory for it
    if not os.path.isdir(portfolio_name):
        os.makedirs(portfolio_name)

    # check if file exists, if yes, add transaction to that file, if not, make it with first entry as this transaction
    file = './' + portfolio_name + '/transaction_summary.csv'
    if os.path.exists(file):
        pd.read_csv(file).append(transaction).to_csv(file, index=False)

    else:
        transaction.to_csv(file, index=False)
