import requests
import pandas as pd


def contains_number(value):
    for character in value:
        if character.isdigit():
            return True
    return False


def get_price(stock, td_option_symbol):

    if not contains_number(td_option_symbol):  # if stock
        endpoint = 'https://api.tdameritrade.com/v1/marketdata/quotes'
        payload = {'apikey': 'WIEVXFCS1MAYRE7JDG5PHF0JB5GPYT8Y',
                   'symbol': stock}

        return pd.json_normalize(requests.get(url=endpoint, params=payload).json())[stock + '.mark'][0]

    else:  # if option
        endpoint = 'https://api.tdameritrade.com/v1/marketdata/chains'
        payload = {'apikey': 'WIEVXFCS1MAYRE7JDG5PHF0JB5GPYT8Y',
                           'symbol': stock,
                           'includeQuotes': 'TRUE',
                           'strategy': 'SINGLE'}

        raw = pd.json_normalize(requests.get(url=endpoint, params=payload).json())

        # Remove all columns related to the underlying stock, leaving only cells containing tables of each contract
        del raw['symbol']
        del raw['status']
        del raw['strategy']
        del raw['interval']
        del raw['isDelayed']
        del raw['isIndex']
        del raw['interestRate']
        del raw['underlyingPrice']
        del raw['volatility']
        del raw['daysToExpiration']
        del raw['numberOfContracts']
        del raw['underlying.symbol']
        del raw['underlying.description']
        del raw['underlying.change']
        del raw['underlying.percentChange']
        del raw['underlying.close']
        del raw['underlying.quoteTime']
        del raw['underlying.tradeTime']
        del raw['underlying.bid']
        del raw['underlying.ask']
        del raw['underlying.last']
        del raw['underlying.mark']
        del raw['underlying.markChange']
        del raw['underlying.markPercentChange']
        del raw['underlying.bidSize']
        del raw['underlying.askSize']
        del raw['underlying.highPrice']
        del raw['underlying.lowPrice']
        del raw['underlying.openPrice']
        del raw['underlying.totalVolume']
        del raw['underlying.exchangeName']
        del raw['underlying.fiftyTwoWeekHigh']
        del raw['underlying.fiftyTwoWeekLow']
        del raw['underlying.delayed']

        option_list = pd.json_normalize(list(raw.loc[0]))  # gets first (and only) row and converts to dataframe

        num_of_contracts = len(option_list.index) - 1  # gets total number of contracts

        option_chain = pd.json_normalize(option_list[0][0])  # converts first contract to dataframe
        # Combines all contracts into one option chain
        for contract in range(1, num_of_contracts):
            option_chain = option_chain.append(pd.json_normalize(option_list[0][contract]))

        contract = option_chain[option_chain['symbol'] == td_option_symbol]

        return contract['mark'][0]
