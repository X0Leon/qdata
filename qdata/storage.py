# -*- coding: utf-8 -*-

"""
存储模块

@author: X0Leon
@version: 0.01
"""

import pandas as pd

class BaseStorage(object):
    """
    存储基类
    """
    def __init__(self, data):
        self.data = data
        self.symbol = list(self.data.keys())[0]


class HDFStorage(BaseStorage):
    """
    HDF5存储
    """
    def __init__(self, data, path):
        super(HDFStorage, self).__init__(data)
        self.storage_type = 'HDF5'
        self.path = path

    def save(self):
        self.data[self.symbol].to_hdf(self.path, self.symbol, format='table', append=True)


class MySQLStorage(BaseStorage):
    """
    MySQL存储
    """
    pass
