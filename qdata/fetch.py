# -*- coding: utf-8 -*-

"""
数据获取模块

@author: X0Leon
@version: 0.1
"""

import tushare as ts
import pandas as pd


def get_bars(symbol, start='', end='', bar_type='D', index=False, retry_count=3, pause=0.001):
    """
    对tushare库的get_k_data()函数浅封装，其使用腾讯财经数据
    参数：
    symbol: 股票或指数的代码，如'600008'
    start: 起始日期，'YYYY-MM-DD'，为空时取上市首日
    end: 结束日期，'YYYY-MM-DD'，为空取最近一个交易日
    bar_type: K bar类型，'D', 'W', 'M', '5', '15', '30', '60'
    index: 是否为指数
    retry_count: 如遇网络等问题重复执行次数
    pause: 若重复执行，其间隔时间
    返回:
    DataFrame的字典，datetime、open、high、low、close、volume

    """
    df = ts.get_k_data(code=symbol, start=start, end=end, ktype=bar_type, autype='qfq',
                       index=False, retry_count=retry_count, pause=pause)
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']].set_index('date')
    df.index.name = 'datetime'
    return {symbol: df}


def get_stock_list():
    """
    返回沪深两市所有的股票列表
    """
    stock_info = ts.get_stock_basics()
    return {'stock_list': sorted(list(stock_info.index))}
