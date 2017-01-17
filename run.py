# -*- coding: utf-8 -*-

from qdata.store import storage


storage(stock_list=['600018'], start='2006-12-01', end='2012-12-01',
        data_type='tick', flag='init', auto=True)
