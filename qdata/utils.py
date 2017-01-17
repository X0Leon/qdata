# -*- coding: utf-8 -*-

"""
各类功能函数

@author: Leon Zhang
"""
import pandas as pd


def hdf_keys(filename, clean=False):
    """ 返回hdf文件的键值 """
    with pd.HDFStore(filename) as store:
       k = store.keys()
    if clean:
        return [s.split('/')[-1] for s in k]
    return k


def duplicate_keys(filename):
    """ 返回重复的keys, 如果返回None说明数据无重复 """
    l = hdf_keys(filename, clean=True)
    duplicates = set([x for x in l if l.count(x) > 1])
    if duplicates:
        return list(duplicates)
    else:
        return None


def ticks_to_bars(ticks, freq='1min'):
    """
    ticks数据合成bars
    参数
    - ticks: 至少包含price, volume列，以datetime为index的DataFrame
    - freq: bars周期，默认为分钟线, '1min'或者'T'
    返回
    - bars: OHLCV的DataFrame, index为datetime格式
    """
    prices = ticks['price'].resample(freq).ohlc()
    prices = prices.dropna()

    volumes = ticks['volume'].resample('1min').sum()
    volumes = volumes.dropna()
    bars = pd.merge(prices, volumes.to_frame('volume'), left_index=True, right_index=True)
    return bars


def to_low_freq(bar_df, freq='5min'):
    """
    bar数据降低频率，例如1分钟变5min, 'D'等
    """
    bars = bar_df.resample(freq, lable='right').agg({'open':'first', 'high':'max',
                                                     'low':'min', 'close':'last', 'volume':'sum'})
    return bars.dropna()


