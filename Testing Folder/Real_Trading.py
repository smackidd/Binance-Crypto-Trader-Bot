from binance import Client
import time as time
import pprint
from datetime import datetime
from configparser import ConfigParser

from binance.helpers import round_step_size
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

API_KEY = config['api']['API_KEY']
SECRET_KEY = config['api']['SECRET_KEY']
print(API_KEY)
print(SECRET_KEY)
client = Client(API_KEY, SECRET_KEY)

print(client.get_account())


# def get_balance(symbol):
#     account = client.get_account()
#     balances = account['balances']
#     amount = 0
#     for balance in balances:
#         if balance['asset'] == symbol:
#             amount = balance['free']
#     return float(amount)


# def get_quantity(symbol):
#     info = client.get_symbol_info(symbol)
#     print(info)
#     symbol_prefix = symbol.replace('USDT', '')
#     amount = get_balance(symbol_prefix)
#     precision = info['quotePrecision']
#     step_size = ''
#     for filter in info['filters']:
#         if filter['filterType'] == 'LOT_SIZE':
#             step_size = float(filter['stepSize'])
#     amt_str = "{:0.0{}f}".format(amount, precision)
#     amount = float(amt_str)
#     rounded_amount = round_step_size(amount, step_size)
#     if rounded_amount > amount:
#         rounded_amount = rounded_amount - step_size
#         rounded_amount = round_step_size(rounded_amount, step_size)
#     return rounded_amount


# def get_quantity(symbol, price):
#     print('here')
#     symbol_prefix = symbol.replace('USDT', '')
#     info = client.get_symbol_info(symbol)
#     pprint.pprint(info)
#     precision = info['quotePrecision']
#     step_size = ''
#     for filter in info['filters']:
#         if filter['filterType'] == 'LOT_SIZE':
#             step_size = float(filter['stepSize'])

#     if type(price) != float:
#         amount = get_balance(symbol_prefix)

#     elif type(price) == float:
#         amount = get_balance('USDT')
#         amount = amount / price

#     amt_str = "{:0.0{}f}".format(amount, precision)
#     amount = float(amt_str)
#     rounded_amount = round_step_size(amount, step_size)
#     if rounded_amount > amount:
#         rounded_amount = rounded_amount - step_size
#         rounded_amount = round_step_size(rounded_amount, step_size)
#     return rounded_amount


# balance = get_balance('USDT')
# print(balance)
# qty = get_quantity('ETHUSDT', 4553.0)
# print(qty)
# order = client.create_order(
#     symbol='ETHUSDT', side='BUY', type='MARKET', quantity=qty)
# print(order)
# time = order['transactTime']
# time = datetime.fromtimestamp(
#     float(time * 0.001)).strftime('%Y-%m-%d %H:%M:%S')
# fills = order['fills']
# price = float(fills[0]['price'])
# print(time)
# print(price)
# print(get_balance('ETH'))
# print(get_balance('USDT'))
# get_balances()
