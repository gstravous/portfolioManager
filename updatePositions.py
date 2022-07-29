import pandas as pd
from getPrice import get_price
import numpy as np
import warnings
import os
import openpyxl
warnings.filterwarnings("ignore")


def update_positions(portfolio_name, cash):
    spreadsheet = pd.ExcelWriter('./' + portfolio_name + '/' + portfolio_name + '_portfolio.xlsx')

    transactions = pd.read_csv('./' + portfolio_name + '/transaction_summary_' + portfolio_name + '.csv')

    transactions.to_excel(spreadsheet, sheet_name='Transaction Summary', index=False)

    if not os.path.exists('./' + portfolio_name + '/position_summary.csv'):  # check if position summary exists, if not, make it
        new_position_summary = pd.DataFrame(
            {'portfolio_name': [], 'position_id': [], 'stock': [], 'shares': [],
             'position_open': [],
             'cost_basis': [], 'purchase_price': [], 'sector': [], 'industry': [],
             'risk': [], 'current_value': [],
             'profit_loss': [], 'ROR': [], 'IRR': []})

        new_position_summary.to_csv('./' + portfolio_name + '/position_summary.csv')

    position_summary_old = pd.read_csv('./' + portfolio_name + '/position_summary.csv')
    closed_positions = position_summary_old[position_summary_old['position_open'] == False]['position_id'].unique()  # list of positions considered closed before current update
    transaction_positions = transactions['position_id'].unique().tolist()  # list of all positions ever traded in portfolio
    if len(closed_positions) > 0:  # if at least one position is closed
        for position in closed_positions:  # remove closed positions
            transaction_positions.remove(position)

    position_summary = position_summary_old[position_summary_old['position_open'] == False]  # dataframe of positions considered closed before current update

    sectors = pd.read_csv('./sectors.csv')

    list_position_values = []  # list of current values of all OPEN positions
    for position in transaction_positions:
        transaction_summary = transactions[transactions['position_id'] == position].reset_index(drop=True)  # dataframe for each position
        transaction_summary['is_open'] = ''
        transaction_summary['current_value'] = np.NAN
        transaction_summary['current_price'] = np.NAN

        securities = transaction_summary['td_option_symbol'].unique()  # list of securities traded in the position

        print(securities)

        list_security_values = []  # list of current value of each security in a position
        security_open = False
        for security in securities:
            security_summary = transaction_summary[transaction_summary['td_option_symbol'] == security].reset_index()  # dataframe for each security
            current_shares = security_summary['shares'].sum()  # current shares owned or short of security
            realized_transactions = security_summary['debit/credit'].sum()

            stock = security_summary['stock'][0]

            if current_shares == 0:  # if security closed
                unrealized_transactions = 0
                transaction_summary['is_open'] = np.where(transaction_summary['td_option_symbol'] == security, False, transaction_summary['is_open'])
                transaction_summary['current_value'] = np.where(transaction_summary['td_option_symbol'] == security,
                                                                np.NAN,
                                                                transaction_summary['current_value'])

            else:  # if security open
                current_price = get_price(stock, security)
                transaction_summary['current_price'] = np.where(transaction_summary['td_option_symbol'] == security,
                                                                current_price, transaction_summary['current_price'])
                unrealized_transactions = current_shares * current_price  # get market value of open position
                security_open = True
                transaction_summary['is_open'] = np.where(transaction_summary['td_option_symbol'] == security, True, transaction_summary['is_open'])
                transaction_summary['current_value'] = np.where(transaction_summary['td_option_symbol'] == security, unrealized_transactions,
                                                          transaction_summary['current_value'])

            security_value = unrealized_transactions + realized_transactions

            list_security_values.append(security_value)

        position_id = transaction_summary['position_id'][0]
        print(position_id)
        stock = transaction_summary['stock'][0]
        shares = abs(transaction_summary['shares'][0])

        if security_open:
            position_open = True
        else:
            position_open = False

        current_stock_price = get_price(stock, 'stock')
        current_expiration = transaction_summary['exp_date'].max()

        try:
            current_strike = transaction_summary[transaction_summary['exp_date'] == current_expiration].reset_index()['strike'][0]
            current_option = transaction_summary[transaction_summary['exp_date'] == current_expiration].reset_index()['put_call'][0]

        except:
            current_strike = np.NAN
            current_option = np.NAN

        transaction_summary['call_open'] = np.where(
            transaction_summary['put_call'] == 'C', np.where(transaction_summary['is_open'], True, False), False)

        if position_open and False in transaction_summary['is_option'].values and True not in transaction_summary['call_open'].values:  # if position is open, stock was bought, and no calls are open
            needs_call = True

        else:
            needs_call = False

        if 'P' in list(transaction_summary['put_call']):
            position_type = 'CSP'

        else:
            position_type = 'BW'

        if (current_option == 'C') & position_open:
            if current_stock_price >= current_strike:
                itm = True
            else:
                itm = False
        elif (current_option == 'P') & position_open:
            if current_stock_price <= current_strike:
                itm = True
            else:
                itm = False

        else:
            itm = np.NAN

        sectors = sectors.astype(str)
        sector_info = sectors[sectors['Ticker'] == stock].reset_index()
        name = sector_info['Company Name'][0]
        sector = sector_info['Sector'][0]
        industry = sector_info['Industry'][0]
        profit_loss = sum(list_security_values)  # current market value of position

        stock_summary = transaction_summary[transaction_summary['is_option'] == False].reset_index(drop=True)  # all stocks in position
        option_summary = transaction_summary[transaction_summary['is_option'] == True].reset_index(drop=True)  # all options in position
        put_summary = option_summary[option_summary['put_call'] == 'P'].reset_index(drop=True)  # all puts in position
        buy_stock = stock_summary[stock_summary['trade_date'] == stock_summary['trade_date'].min()].reset_index(drop=True)  # first buy of stock
        first_option = option_summary[option_summary['trade_date'] == option_summary['trade_date'].min()].reset_index(drop=True) # first option trade

        if put_summary.empty:  # if buy write
            cost_basis = buy_stock['price'][0] - option_summary['price'].sum()
            purchase_price = buy_stock['price'][0]
            try:
                risk = (buy_stock['debit/credit'][0] + first_option['debit/credit'][0]) * -1

            except:
                risk = buy_stock['debit/credit'][0] * -1

        else:  # if put
            cost_basis = first_option['strike'][0] - option_summary['price'].sum()
            purchase_price = first_option['strike'][0]
            risk = (first_option['strike'][0] - first_option['price'][0]) * shares

        #current_value = risk + profit_loss
        current_value = transaction_summary['current_value'].sum()

        if (current_option == 'P') & position_open:
            current_value = current_value + (shares * current_strike)
            cash = cash - (shares * current_strike)

        ror = profit_loss / risk

        def days_to_exp(start_date, end_date):
            np.busday_count(start_date,
                            end_date,
                            weekmask='1111100',
                            holidays=[np.datetime64('2022-01-17'),
                                      np.datetime64('2022-02-21'),
                                      np.datetime64('2022-05-30'),
                                      np.datetime64('2022-09-05'),
                                      np.datetime64('2022-11-24'),
                                      np.datetime64('2022-04-15'),
                                      np.datetime64('2023-01-16'),
                                      np.datetime64('2023-02-20'),
                                      np.datetime64('2023-05-29'),
                                      np.datetime64('2023-09-04'),
                                      np.datetime64('2023-11-23'),
                                      np.datetime64('2023-04-07'),
                                      np.datetime64('2024-01-15'),
                                      np.datetime64('2024-02-19'),
                                      np.datetime64('2024-05-27'),
                                      np.datetime64('2024-09-02'),
                                      np.datetime64('2024-11-28'),
                                      np.datetime64('2024-03-29')])

        first_date = transaction_summary[transaction_summary['trade_date'] == transaction_summary['trade_date'].min()]
        last_date = transaction_summary[transaction_summary['trade_date'] == transaction_summary['trade_date'].min()]
        today = np.datetime64('today', 'D')

        # if position_open:
        #     irr = (ror / days_to_exp(pd.to_datetime(first_date['trade_date'][0], format='%y%m%d'), today)) * 252
        #
        # else:
        #     irr = (ror / days_to_exp(pd.to_datetime(first_date['trade_date'][0], format='%y%m%d'), pd.to_datetime(last_date['trade_date'][0], format='%y%m%d'))) * 252


        position = pd.DataFrame(
            {'portfolio_name': [portfolio_name], 'position_id': [position_id], 'stock': [stock], 'name': [name], 'position_type': [position_type], 'shares': [shares], 'position_open': [position_open], 'current_stock_price': [current_stock_price],
             'cost_basis': [cost_basis], 'purchase_price': [purchase_price], 'sector': [sector], 'industry': [industry], 'risk': [risk], 'current_value': [current_value],
             'profit_loss': [profit_loss], 'ROR': [ror], 'IRR': ['irr'], 'needs_call': [needs_call], 'current_expiration': [current_expiration], 'current_strike': [current_strike], 'current_option': [current_option], 'itm': [itm]})

        if position_open:
            list_position_values.append(current_value)

        print(list_position_values)

        position_summary = position_summary.append(position)

    position_summary = position_summary[['portfolio_name', 'position_id', 'stock', 'name', 'shares', 'position_open',
                                         'current_stock_price', 'cost_basis', 'purchase_price', 'current_strike',
                                         'current_option', 'current_expiration', 'sector', 'industry', 'risk',
                                         'current_value', 'profit_loss', 'ROR', 'IRR', 'position_type', 'itm',
                                         'needs_call']]

    position_summary.to_csv('./' + portfolio_name + '/position_summary.csv', index=False)

    position_summary.to_excel(spreadsheet, sheet_name='Position Summary', index=False)

    portfolio_value = sum(list_position_values) + cash

    consumer_defensive = position_summary[position_summary['sector'] == 'Consumer Defensive']['current_value'].sum()
    healthcare = position_summary[position_summary['sector'] == 'Healthcare']['current_value'].sum()
    industrials = position_summary[position_summary['sector'] == 'Industrials']['current_value'].sum()
    consumer_cyclical = position_summary[position_summary['sector'] == 'Consumer Cyclical']['current_value'].sum()
    financial_services = position_summary[position_summary['sector'] == 'Financial Services']['current_value'].sum()
    technology = position_summary[position_summary['sector'] == 'Technology']['current_value'].sum()
    basic_materials = position_summary[position_summary['sector'] == 'Basic Materials']['current_value'].sum()
    utilities = position_summary[position_summary['sector'] == 'Utilities']['current_value'].sum()
    business_services = position_summary[position_summary['sector'] == 'Business Services']['current_value'].sum()
    real_estate = position_summary[position_summary['sector'] == 'Real Estate']['current_value'].sum()
    energy = position_summary[position_summary['sector'] == 'Energy']['current_value'].sum()

    sector_allocation = pd.DataFrame({'sector': ['Consumer Defensive', 'Healthcare', 'Industrials', 'Consumer Cyclical', 'Financial Services', 'Technology', 'Basic Materials', 'Utilities', 'Business Services', 'Real Estate', 'Energy', 'CASH'], 'allocation': [consumer_defensive, healthcare, industrials, consumer_cyclical, financial_services, technology, basic_materials, utilities, business_services, real_estate, energy, cash]})

    sector_allocation['percentage'] = sector_allocation['allocation'] / portfolio_value

    sector_allocation['goal'] = [.08333, .08333, .08333, .08333, .08333, .08333, .08333, .08333, .08333, .08333, .08333, .08333]

    sector_allocation['cash_goal'] = sector_allocation['goal'] * portfolio_value

    sector_allocation['add_or_reduce'] = sector_allocation['cash_goal'] - sector_allocation['allocation']

    sector_allocation.to_excel(spreadsheet, sheet_name='Sector Allocation', index=False)

    spreadsheet.save()

    return portfolio_value


print(update_positions('CI', 12078.82))
#print(update_positions('MAIN', 84284.09))

