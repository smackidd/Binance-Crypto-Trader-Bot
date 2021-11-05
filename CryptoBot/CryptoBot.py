from configparser import ConfigParser

import websocket
import pprint
import numpy
import json
import pandas as pd
#import ta
from binance import Client
from binance.helpers import round_step_size
import time as time
from datetime import datetime
secret_config_file = 'secret_config.ini'
secret_config = ConfigParser()
secret_config.read(secret_config_file)

API_KEY = secret_config['api']['API_KEY']
SECRET_KEY = secret_config['api']['SECRET_KEY']


class TestTradingEnv:
    def __init__(self, balance_amount, balance_unit, trading_fee_multiplier):
        self.balance_amount = balance_amount
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []
        # VIP level 0, paying fees with BNB
        self.trading_fee_multiplier = trading_fee_multiplier

    def buy(self, symbol, buy_price, time):
        self.balance_amount = self.balance_amount / \
            buy_price * self.trading_fee_multiplier
        self.balance_unit = symbol
        time = datetime.fromtimestamp(
            float(time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        self.buys.append(
            {"symbol": symbol, "time": time, "Buy Price": buy_price})
        print("You just bought {} {} at {}".format(
            self.balance_amount, symbol, time))
        print(f'Your {symbol} is worth ${buy_price * self.balance_amount} USDT')
        self.output_to_csv()

    def sell(self, sell_price, time):
        self.balance_amount = self.balance_amount * \
            sell_price * self.trading_fee_multiplier
        time = datetime.fromtimestamp(
            float(time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        self.sells.append({"symbol": self.balance_unit,
                          "time": time, "Sell Price": sell_price})
        print("You just sold {} for {} at {}".format(
            self.balance_unit, self.balance_amount, time))
        print(f'You have ${self.balance_amount} USDT')
        self.balance_unit = 'USDT'
        self.output_to_csv()

    def output_to_csv(self):
        if len(self.sells) > 0:
            sells_df = pd.DataFrame(self.sells)
        if len(self.buys) > 0:
            buys_df = pd.DataFrame(self.buys)

        if len(self.sells) > 0 and len(self.buys) > 0:
            frames = [buys_df, sells_df]
            csv_df = pd.concat(frames, keys='time')
            # csv_df = pd.merge(buys_df, sells_df, how='inner', on='time' index='time')
            print(csv_df)
            csv_df.to_csv('Double Bottoms Crypto Bot Buys_Sells.csv')
            print('output to csv')


class RealTradingEnv:
    def __init__(self, api_key, secret_key, balance_unit):
        self.client = Client(api_key, secret_key)
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []

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


class Strategy:
    def __init__(self, strategy):
        self.strategy = strategy
        self.double_bottom_count = 0
        self.double_top_count = 0
        self.dipped_below = True
        self.dipped_above = True

    def implement_strategy(self, account, coin_kline, kline_close, close_time):
        #print(f"implement strategy...strategy: {self.strategy}")
        if self.strategy == "bollinger bands":
            self.bollinger_bands(account, coin_kline, kline_close, close_time)
        if self.strategy == "double bottom":
            self.double_bottom(account, coin_kline, kline_close, close_time)

    def bollinger_bands(self, account, coin_kline, kline_close, close_time):
        if account.balance_unit == "USDT":
            if float(kline_close) < coin_kline.lower_band:
                account.buy('ETHUSDT', float(kline_close), close_time)
        if account.balance_unit != "USDT":
            if float(kline_close) > coin_kline.upper_band and coin_kline.upper_band != 0:
                print("sell?")
                account.sell(float(kline_close), close_time)

    def double_bottom(self, account, coin_kline, kline_close, close_time):
        #print("double bottom...")
        if account.balance_unit == "USDT":
            print(
                f'buy test...double_bottom_count: {self.double_bottom_count}, dipped_above: {self.dipped_above}')
            if float(kline_close) < coin_kline.lower_band and coin_kline.upper_band != 0:
                if self.double_bottom_count >= 1 and self.dipped_above == True:
                    print("hit 2nd bottom...buying...")
                    account.buy('ETHUSDT', float(kline_close), close_time)
                    self.double_bottom_count = 0
                elif self.dipped_above == True:
                    print("hit 1st bottom...")
                    self.double_bottom_count = self.double_bottom_count + 1
                    self.dipped_above = False
            elif self.dipped_above == False and self.double_bottom_count > 0:
                self.dipped_above = True
        if account.balance_unit != "USDT":
            #print("sell test...")
            if float(kline_close) > coin_kline.upper_band and coin_kline.upper_band != 0:
                if self.double_top_count >= 1 and self.dipped_below == True:
                    print("hit 2nd top...selling...")
                    account.sell(float(kline_close), close_time)
                    self.double_top_count = 0
                elif self.dipped_below == True:
                    print("hit 1st top...")
                    self.double_top_count = self.double_top_count + 1
                    print(f'double top count: {self.double_top_count}')
                    self.dipped_below = False
                    print(f'dipped below: {self.dipped_below}')
            elif self.dipped_below == False and self.double_top_count > 0:
                self.dipped_below = True
                print(f'dipped below: {self.dipped_below}')


class Coin:
    def __init__(self, coin_unit):
        self.coin_unit = coin_unit
        self.candles = []
        self.sma = 0
        self.upper_band = 0
        self.lower_band = 0

    def get_klines(self, kline_open, kline_close, high, low, open_time, close_time):
        # print('here')
        open_datetime = datetime.fromtimestamp(
            float(open_time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        close_datetime = datetime.fromtimestamp(
            float(close_time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
        print(open_datetime)
        kline = {
            'open': float(kline_open),
            'close': float(kline_close),
            'high': float(high),
            'low': float(low),
            'open_time': open_datetime,
            'close_time': close_datetime
        }
        self.candles.append(kline)
        # print(self.candles)
        self.simpleMovingAverage()
        #print("getting klines")
        # print(kline)

    def simpleMovingAverage(self):
        #print('simple moving average')
        # closes = [4289.05, 4281.21, 4280.90, 4275.85, 4277.91, 4285.85, 4292.01, 4288.88, 4287.81, 4281.50,
        #          4277.99, 4273.40, 4271.89, 4272.01, 4271.90, 4277.65, 4280.34, 4285.55, 4292.00, 4295.00]
        closes = []
        nStandardDeviation = 2
        for candle in self.candles:
            closes.append(candle['close'])
        # print(closes)
        closes_df = pd.DataFrame(closes)

        # rolling window is 21, so don't calculate sma until you have 20 items in array
        if len(closes) >= 21:
            closes_df['sma'] = closes_df[0].rolling(window=21).mean()
            self.sma = closes_df['sma'].iloc[-1].astype(float)
            # print(self.sma)
            closes_df['upper_band'], closes_df['lower_band'] = self.bollinger_band(
                closes_df[0], closes_df['sma'], 21, nStandardDeviation)

            self.upper_band = closes_df['upper_band'].iloc[-1].astype(float)
            self.lower_band = closes_df['lower_band'].iloc[-1].astype(float)

            print(f'Upper band: {self.upper_band}')
            print(f'Lower band: {self.lower_band}')

    def bollinger_band(self, data, sma, window, nStandardDeviation):
        standardDeviation = data.rolling(window=window).std()
        upperBand = sma + standardDeviation * nStandardDeviation
        lowerBand = sma - standardDeviation * nStandardDeviation
        return upperBand, lowerBand


DURATION = '15m'
COIN_UNIT = 'ETHUSDT'
#STRATEGY = "bollinger bands"
STRATEGY = "double bottom"
coin_kline = Coin(coin_unit=COIN_UNIT)
#account = TestTradingEnv(0.020773, 'ETHUSDT', trading_fee_multiplier=0.99925)
account = RealTradingEnv(API_KEY, SECRET_KEY, COIN_UNIT)
coin_unit_prefix = COIN_UNIT.replace('USDT', '')
print(
    f'You started with {account.get_balance(coin_unit_prefix)} {coin_unit_prefix}')
buy_sell = Strategy(strategy=STRATEGY)
print(coin_kline.coin_unit)


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, msg):
    json_message = json.loads(msg)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    # print(is_candle_closed)
    kline_open = candle['o']
    kline_close = candle['c']
    high = candle['h']
    low = candle['l']
    open_time = candle['t']
    close_time = candle['T']
    coin = candle['s']
    #print("ETHUSDT: {}".format(kline_close))

    # handle kline retrieval and updating sma and bollinger bands
    if is_candle_closed:
        print("candle close at {} for {}".format(kline_close, coin))
        coin_kline.get_klines(kline_open, kline_close,
                              high, low, open_time, close_time)

    # handle buy / sell conditions
    buy_sell.implement_strategy(account, coin_kline, kline_close, close_time)


SOCKET = f'wss://stream.binance.com:9443/ws/ethusdt@kline_{DURATION}'
ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
