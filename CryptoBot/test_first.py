import unittest
from datetime import datetime
import time
from TradingEnv import TestTradingEnv


class TestBuy(unittest.TestCase):
    def test_buy(self):
        account = TestTradingEnv(0.025749, 'ETHUSDT', 0.99925)

        def run_buy():
            account.sell(4500, int(time.time()))
            balance = account.balance_amount
            return balance

        self.assertEquals(run_buy(), 115.783597125)
