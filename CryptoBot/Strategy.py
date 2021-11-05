

class Strategy:
    def __init__(self, strategy):
        self.strategy = strategy
        self.double_bottom_count = 0
        self.double_top_count = 0
        self.dipped_below = True
        self.dipped_above = True

    def implement_strategy(self, account, coin_kline, kline_close, close_time):
        #print(f"implement strategy...strategy: {self.strategy}")
        if self.strategy == "bollinger_bands":
            self.bollinger_bands(account, coin_kline, kline_close, close_time)
        if self.strategy == "double_bottom":
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
            # print(
            #    f'buy test...double_bottom_count: {self.double_bottom_count}, dipped_above: {self.dipped_above}')
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
