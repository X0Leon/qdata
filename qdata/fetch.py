# -*- coding: utf-8 -*-

"""
数据获取模块，ticK或bar频率

@author: Leon Zhang
"""

import re
import datetime

import requests
import tushare as ts
import pandas as pd


def get_stock_info():
    """
    返回沪深两市所有的股票及其上市时间
    """
    stock_info = ts.get_stock_basics()
    stock_info = stock_info[['timeToMarket']]
    stock_info.index.name = 'symbol'

    return {'stock_list': list(stock_info.index),
            'to_market': list(stock_info)}


def get_stock_list(source='tushare'):
    """
    返回沪深两市所有的股票列表
    """
    if source == 'shdjt':
        # 'http://www.shdjt.com'
        all_stock_codes_url = 'http://www.shdjt.com/js/lib/astock.js'
        grep_stock_codes = re.compile('~(\d+)`')
        response = requests.get(all_stock_codes_url)
        stock_list = grep_stock_codes.findall(response.text)
        return stock_list
    else:
        # tushare
        stock_info = ts.get_stock_basics()
        return sorted(list(stock_info.index))


def get_bars_netease(symbol, start='', end=''):
    """
    网易财经数据源，只能获得日线数据
    示例：http://quotes.money.163.com/service/chddata.html?code=600008&start=20150508&end=20150512
    参数：
    - symbol: 股票或指数的代码，如'600008'
    - start: 起始日期，'YYYY-MM-DD'，为空时取上市首日
    - end: 结束日期，'YYYY-MM-DD'，为空取最近一个交易日
    返回:
    字典，key是symbol，value为datetime、open、high、low、close、volume的DataFrame
    """
    if not start:
        start = (datetime.datetime.now().date() + datetime.timedelta(days=-300)).strftime('%Y-%m-%d')
    if not end:
        end = datetime.datetime.now().date().strftime('%Y-%m-%d')
    start = start.replace('-', '')
    end = end.replace('-', '')
    data_url = "http://quotes.money.163.com/service/chddata.html?code=0" + symbol + "&start=" + start + "&end=" + end
    r = requests.get(data_url, stream=True)
    lines = r.content.decode('gb2312').split("\n")
    lines = lines[1:len(lines) - 1]
    bars = []
    for line in lines[::-1]:
        stock_info = line.split(",", 14)
        s_date = stock_info[0]
        s_close = stock_info[3]
        s_high = stock_info[4]
        s_low = stock_info[5]
        s_open = stock_info[6]
        s_volume = stock_info[11]
        bars.append([s_date, s_open, s_high, s_low, s_close, s_volume])
    bars = pd.DataFrame(bars, columns=['datetime', 'open', 'high', 'low', 'close', 'volume']).set_index('datetime')

    return bars


def get_bars_tushare(symbol, start='', end='', bar_type='D', index=False, retry_count=3, pause=0.001):
    """
    对tushare库的get_k_data()函数浅封装，其使用腾讯财经数据
    参数：
    - symbol: 股票或指数的代码，如'600008'
    - start: 起始日期，'YYYY-MM-DD'，为空时取上市首日
    - end: 结束日期，'YYYY-MM-DD'，为空取最近一个交易日
    - bar_type: K bar类型，'D', 'W', 'M', '5', '15', '30', '60'
    - index: 是否为指数
    - retry_count: 如遇网络等问题重复执行次数
    - pause: 若重复执行，其间隔时间

    返回:
    - 字典，key是symbol，value为datetime、open、high、low、close、volume的DataFrame

    """
    df = ts.get_k_data(code=symbol, start=start, end=end, ktype=bar_type, autype=None,
                       index=index, retry_count=retry_count, pause=pause)
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']].set_index('date')
    df.index.name = 'datetime'
    return df


def get_ticks_tushare(symbol, date, retry_count=3, pause=0.001, drop_auction=True):
    """
    使用tushare(来自sina数据源)库获取tick数据
    参数
    - symbol: 股票或指数的代码，如'600008'
    - date: 日期格式，'YYYY-MM-DD'
    - retry_count: 如遇网络等问题重复执行的次数
    - pause: 重复请求数据过程中暂停的秒数
    - drop_auction: 是否剔除竞价数据
    """
    df = ts.get_tick_data(code=symbol, date=date, retry_count=retry_count, pause=pause)
    if len(df) < 4:
        return None
    else:
        df['time'] = date + ' ' + df['time']
        df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')
        df = df.set_index('time')
        df.index.name = 'datetime'
        if drop_auction:
            return df.sort_index()[1:]
        else:
            return df.sort_index()


def get_auth_factor(symbol, start=None, end=None, retry_count=3, pause=0.001):
    """
    获取股票后复权因子
    """
    df = ts.get_h_data(symbol, start=start, end=end, retry_count=retry_count, pause=pause, drop_factor=False)
    df.index.name = 'datetime'
    return df['factor'].to_frame().sort_index()
