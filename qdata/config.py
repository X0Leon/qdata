# -*- coding: utf-8 -*-

"""
配置模块

@author: X0Leon
@version: 0.01
"""

import logging
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), 'out')
NUM_THREADERS = 10

LOG = {'ROOT_LEVEL': logging.INFO,
       'CONSOLE_LEVEL': logging.INFO,
       'FILE_LEVEL': logging.INFO,
       'TO_FILE': False}

STORAGE = {'TO_FILE': 'daily.h5',
           'STOCK_FILE': 'stock_list.pkl'}
