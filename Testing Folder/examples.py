import time
from datetime import datetime
from binance import Client
from configparser import ConfigParser
from RealTradingEnv import RealTradingEnv
from Strategy import Strategy
from Coin import Coin
import sys


secret_config_file = 'secret_config.ini'
secret_config = ConfigParser()
secret_config.read(secret_config_file)

API_KEY = secret_config['api']['API_KEY']
SECRET_KEY = secret_config['api']['SECRET_KEY']


account = RealTradingEnv(API_KEY, SECRET_KEY, 'ETHUSDT')
coin_kline = Coin(coin_unit='ETHUSDT')
buy_sell = Strategy(strategy='bollinger_bands')

# klines = account.get_recent_klines(symbol='ETHUSDT', duration='1m', limit=21)
# # print(klines)

# price = float(klines[-1][4])
# close_time = klines[-1][6]
# print(price)

upper_bands = [15, -5, 15, 35]
lower_bands = [-15, -35, -15, 5]

for y in range(3):
    for x in range(4):
        klines = account.get_recent_klines(
            symbol='ETHUSDT', duration='1m', limit=5)
        # print(klines)

        price = float(klines[-1][4])
        close_time = klines[-1][6]
        print(price)
        coin_kline.upper_band = upper_bands[x] + price
        print(f'upper_band: {coin_kline.upper_band}')
        coin_kline.lower_band = lower_bands[x] + price
        print(f'lower_band: {coin_kline.lower_band}')
        buy_sell.implement_strategy(account, coin_kline, price, close_time)
        time.sleep(1)
