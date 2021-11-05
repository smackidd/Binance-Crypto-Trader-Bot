from datetime import datetime
import pandas as pd


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
