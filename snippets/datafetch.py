# -*- coding: utf-8 -*-

"""
Remote Data Access 远程数据获取存储成CSV或HDF5格式

Python库：
1) pandas_datareader（0.19以前的pandas.io的data, web）
2) TuShare
底层数据源：a) Yahoo! Finance; 2) 新浪等

@author: X0Leon
"""

import re
import requests


def get_stock_type(stock_code):
    """
    判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    参数：
    stock_code: 股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    return 'sh' or 'sz'
    """
    assert type(stock_code) is str, 'stock code need str type'
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '90', '110', '113', '132', '204')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'


def get_all_stock_codes():
    """获取所有股票 ID"""
    all_stock_codes_url = 'http://www.shdjt.com/js/lib/astock.js'
    grep_stock_codes = re.compile('~(\d+)`')
    response = requests.get(all_stock_codes_url)
    stock_codes = grep_stock_codes.findall(response.text)
    return stock_codes