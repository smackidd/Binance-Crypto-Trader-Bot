import unittest
from datetime import datetime
import time
from RealTradingEnv import RealTradingEnv
from TradingEnv import TestTradingEnv
from Strategy import Strategy
from Coin import Coin
from configparser import ConfigParser
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)
secret_config_file = 'secret_config.ini'
secret_config = ConfigParser()
secret_config.read(secret_config_file)

# DURATION = config['settings']['DURATION']
COIN_UNIT = config['settings']['COIN_UNIT']
# #STRATEGY = "bollinger bands"
# STRATEGY = config['settings']['STRATEGY']

API_KEY = secret_config['api']['API_KEY']
SECRET_KEY = secret_config['api']['SECRET_KEY']


class TestStrategy(unittest.TestCase):
    def test_bollinger_bands(self):
        account = RealTradingEnv(API_KEY, SECRET_KEY, COIN_UNIT)
        coin_kline = Coin(coin_unit=COIN_UNIT)
        buy_sell = Strategy(strategy='bollinger_bands')

        # Manufacture fake upper and lower bands based on current price
        upper_bands = [15, -5, 15, 35]
        lower_bands = [-15, -35, -15, 5]

        # to trigger buys and sells

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
            if x == 0:
                print("first test")
                self.assertEqual(account.balance_unit, COIN_UNIT)
            elif x == 1:
                print("second test")
                self.assertEqual(account.balance_unit, 'USDT')
            elif x == 2:
                print("third test")
                self.assertEqual(account.balance_unit, 'USDT')
            elif x == 3:
                print("fourth test")
                self.assertEqual(account.balance_unit, COIN_UNIT)

            time.sleep(1)
