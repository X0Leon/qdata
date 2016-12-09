# -*- coding: utf-8 -*-

"""
网易

@author: X0Leon
"""

STOCK_TODAY = 'http://img1.money.126.net/data/hs/time/current_dt/%s%s.json' # exchange, code
STOCK_HISTORY = 'http://img1.money.126.net/data/hs/kline/day/times/%s%s.json' # exchange, code
STOCK_HISTORY_ADJ = 'http://img1.money.126.net/data/hs/klinederc/day/history/%s/%s%s.json' # year, exchange, code


from datetime import datetime
from urllib.request import urlopen

import json

def exchange_to_num(exchange_str):
    if exchange_str == 'ss':
        return 0
    elif exchange_str == 'sz':
        return 1
    else:
        raise NameError('Exchange name is not correct')

def get_json(url):
    try:
        response = urlopen(url)
    except:
        return None
    data = json.loads(response.read().decode())
    return data

def get_stock_today(code, exchange):
    exchange = exchange_to_num(exchange)
    url = STOCK_TODAY % (exchange, code)
    data = get_json(url)  # 包含’count', 'data', 'date', 'lastVolume', 'name', 'symbol', 'yestclose'的字典
    price = data['data']
    date = data['date']
    res = [[date + d[0], d[1], d[3]] for d in price]
    return res

def get_stock_history(code, exchange):
    exchange = exchange_to_num(exchange)
    url = STOCK_HISTORY % (exchange, code)
    data = get_json(url)
    times = data['times']
    closes = data['closes']
    res = [[t, c] for (t, c) in zip(times, closes)]
    return res

def get_stock_history_adj(code, exchange, year=None):
    if not year:
        year = datetime.now().year
    exchange = exchange_to_num(exchange)
    url = STOCK_HISTORY_ADJ % (year, exchange, code)
    data = get_json(url)
    prices = data['data']
    res = prices
    return res

if __name__ == "__main__":
    print(get_stock_today(code='000005', exchange='sz'))
