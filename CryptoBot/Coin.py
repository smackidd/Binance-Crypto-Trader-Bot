from configparser import ConfigParser
from datetime import datetime
import pandas as pd
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)


class Coin:
    def __init__(self, coin_unit):
        self.coin_unit = coin_unit
        self.candles = []
        self.sma = 0
        self.upper_band = 0
        self.lower_band = 0
        self.nStandardDeviation = float(
            config['settings']['N_STANDARD_DEVIATION'])
        self.rolling_average = float(config['settings']['ROLLING_AVERAGE'])

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
        nStandardDeviation = self.nStandardDeviation
        for candle in self.candles:
            closes.append(candle['close'])
        # print(closes)
        closes_df = pd.DataFrame(closes)

        # rolling window is 21, so don't calculate sma until you have 20 items in array
        if len(closes) >= self.rolling_average:
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
