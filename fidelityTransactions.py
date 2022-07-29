import pandas as pd
import numpy as np


def fidelity_transactions(portfolio_name):
    raw = pd.read_csv('./' + portfolio_name + '/raw.csv', header=1).dropna(subset=['Quantity'])

    del raw['Commission ($)']
    del raw['Fees ($)']
    del raw['Accrued Interest ($)']
    del raw['Settlement Date']

    raw['Portfolio'] = 'MAIN'
    raw['Position'] = ''

    symbols = []
    expiration_dates = []
    call_puts = []
    strikes = []
    is_options = []
    for symbol in raw['Symbol']:
        if '-' in symbol:
            symbol = symbol.replace('-', '')
            is_option = True

        else:
            is_option = False

        print(symbol)

        stock = True
        date = True
        stock_symbol = []
        expiration_date = []
        call_put = []
        strike_price = []
        for character in symbol:
            if not (('0' <= character <= '9') or (character == '.')):  # if letter
                if stock:  # if stock symbol
                    stock_symbol.append(character)

                if not stock:  # if call or put
                    date = False
                    call_put.append(character)

            else:  # if number or decimal
                stock = False
                if date:  # if expiration date
                    expiration_date.append(character)

                if not date:  # if strike price
                    strike_price.append(character)

        stock_symbol = ''.join(stock_symbol).replace(' ', '')
        expiration_date = ''.join(expiration_date)
        call_put = ''.join(call_put)
        strike_price = ''.join(strike_price)

        symbols.append(stock_symbol)
        expiration_dates.append(expiration_date)
        call_puts.append(call_put)
        strikes.append(strike_price)
        is_options.append(is_option)

    raw['Stock'] = symbols
    raw['Expiration Date'] = expiration_dates
    raw['Call Put'] = call_puts
    raw['Strike'] = strikes
    raw['Is Option'] = is_options

    raw['Run Date'] = raw['Run Date'].str[9:11] + raw['Run Date'].str[1:3] + raw['Run Date'].str[4:6]

    raw['Year'] = raw['Expiration Date'].str[:2]
    raw['Month'] = raw['Expiration Date'].str[2:4]
    raw['Day'] = raw['Expiration Date'].str[4:6]

    raw['Expiration Date'] = raw['Year'] + raw['Month'] + raw['Day']

    raw['TD Symbol'] = raw['Stock'] + '_' + raw['Month'] + raw['Day'] + raw['Year'] + raw['Call Put'] + raw['Strike']

    raw['Quantity'] = np.where(raw['Is Option'], raw['Quantity'] * 100, raw['Quantity'])

    raw = raw.reindex(
        columns=['Action', 'Security Description', 'Security Type', 'Symbol', 'Portfolio', 'Position', 'Stock', 'Month', 'Day', 'Year', 'Call Put', 'Strike', 'Quantity', 'Price ($)', 'Run Date', 'Amount ($)', 'TD Symbol', 'Expiration Date', 'Is Option'])

    raw.to_csv('./' + portfolio_name + '/new_transactions.csv')


fidelity_transactions('MAIN')
