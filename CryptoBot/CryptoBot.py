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

from TradingEnv import TestTradingEnv
from RealTradingEnv import RealTradingEnv
from Strategy import Strategy
from Coin import Coin

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)
secret_config_file = 'secret_config.ini'
secret_config = ConfigParser()
secret_config.read(secret_config_file)

DURATION = config['settings']['DURATION']
COIN_UNIT = config['settings']['COIN_UNIT']
#STRATEGY = "bollinger bands"
STRATEGY = config['settings']['STRATEGY']

API_KEY = secret_config['api']['API_KEY']
SECRET_KEY = secret_config['api']['SECRET_KEY']


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
