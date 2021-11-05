from datetime import datetime
import pandas as pd
from binance import Client
from binance.helpers import round_step_size


class RealTradingEnv:
    def __init__(self, api_key, secret_key, balance_unit):
        self.client = Client(api_key, secret_key)
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []

    def get_recent_klines(self, symbol, duration, limit):
        print("getting recent klines")
        return self.client.get_klines(symbol=symbol, interval=duration, limit=limit)

    def get_balance(self, symbol):
        binance_account = self.client.get_account()
        amount = 0
        for balance in binance_account['balances']:
            if balance['asset'] == symbol:
                amount = balance['free']
                break
        return float(amount)

    def get_quantity(self, symbol, price):
        print('here')
        symbol_prefix = symbol.replace('USDT', '')
        info = self.client.get_symbol_info(symbol)
        # pprint.pprint(info)
        precision = info['quotePrecision']
        step_size = ''
        for filter in info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])

        if type(price) != float:
            amount = self.get_balance(symbol_prefix)
            print(f'amount of {symbol}: {amount}')

        elif type(price) == float:
            base_amount = self.get_balance('USDT')
            amount = base_amount / price
            print(f'amount of {symbol}: {amount}')

        amt_str = "{:0.0{}f}".format(amount, precision)
        amount = float(amt_str)
        rounded_amount = round_step_size(amount, step_size)
        if rounded_amount > amount:
            rounded_amount = rounded_amount - step_size
            rounded_amount = round_step_size(rounded_amount, step_size)
        print(f'rounded_amount: {rounded_amount}')
        return rounded_amount

    def buy(self, symbol, buy_price, time):
        # create order
        print(f'buying...symbol: {symbol}')
        symbol_prefix = symbol.replace('USDT', '')
        qty = self.get_quantity(symbol, buy_price)
        print(f'order: symbol {self.balance_unit}, quantity {qty}')
        order = self.client.create_order(
            symbol=symbol, side='BUY', type='MARKET', quantity=qty)
        print(order)
        # append info to self.buys
        self.balance_unit = symbol
        time = order['transactTime']
        time = datetime.fromtimestamp(
            float(time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        fills = order['fills']
        price = float(fills[0]['price'])
        # get balance amount of symbol
        self.balance_amount = self.get_balance(symbol_prefix)
        self.buys.append(
            {"symbol": symbol, "time": time, "Buy Price": price, "Quantity": qty})

        # log to console
        print("You just bought {} {} at {}".format(
            self.balance_amount, symbol, time))
        print(f'Your {symbol} is worth ${price * self.balance_amount} USDT')
        self.output_to_csv()

    def sell(self, sell_price, time):
        # self.balance_amount = self.balance_amount * \
        #     sell_price * self.trading_fee_multiplier
        print(f'selling...self.balance_unit{self.balance_unit}')
        symbol_prefix = self.balance_unit.replace('USDT', '')
        qty = self.get_quantity(self.balance_unit, price='none')
        print(f'order: symbol {self.balance_unit}, quantity {qty}')
        order = self.client.create_order(
            symbol=self.balance_unit, side='SELL', type='MARKET', quantity=qty)
        print(order)
        time = order['transactTime']
        time = datetime.fromtimestamp(
            float(time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        fills = order['fills']
        price = float(fills[0]['price'])
        self.balance_amount = self.get_balance('USDT')
        self.sells.append({"symbol": self.balance_unit,
                          "time": time, "Sell Price": price, "Quantity": qty})
        print("You just sold {} for {} at {}".format(
            self.balance_unit, self.balance_amount, time))
        print(f'You have ${self.balance_amount} USDT')
        self.balance_unit = 'USDT'
        self.output_to_csv()

    def output_to_csv(self):
        print('output to csv check ....')
        if len(self.sells) > 0:
            sells_df = pd.DataFrame(self.sells)
        if len(self.buys) > 0:
            buys_df = pd.DataFrame(self.buys)

        if len(self.sells) > 0 and len(self.buys) > 0:
            frames = [buys_df, sells_df]
            csv_df = pd.concat(frames, keys='time')
            # csv_df = pd.merge(buys_df, sells_df, how='inner', on='time' index='time')
            print(csv_df)
            csv_df.to_csv('Real Trading Crypto Bot Buys_Sells')
            print('output to csv')
