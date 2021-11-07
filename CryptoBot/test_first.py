import unittest
from datetime import datetime
import time
from TradingEnv import TestTradingEnv
from Coin import Coin


class TestBuy(unittest.TestCase):
    def test_buy(self):
        coin = Coin('ETHUSDT')

        self.assertEquals(coin.rolling_average, 21)
