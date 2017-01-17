# -*- coding: utf-8 -*-

"""
数据获取、存储的中心调度模块

@author: Leon Zhang
"""
try:
    import queue
except ImportError:
    import Queue as queue

import os
import pickle
import pandas as pd
import datetime
from threading import Thread

from .fetch import get_ticks_tushare, get_stock_info, get_auth_factor
from .utils import hdf_keys

import warnings
warnings.filterwarnings('ignore')


OUT_PATH = os.path.join(os.path.dirname(__file__), 'out')
NUM_THREAD = 10
STORAGE = {'STOCK_FILE': 'stock_list.pkl',
           'TO_MARKET_FILE': 'to_market.pkl',
           'Tick': 'tick_data',
           'Factor': ''}


class Worker(Thread):
    """
    用于从队列tasks执行任务的线程
    """
    def __init__(self, tasks):
        super(Worker, self).__init__()
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                # 当前线程异常
                print('Error: ', e)
            finally:
                # 无论是否异常，标记此线程任务完成
                self.tasks.task_done()


class ThreadPool:
    """
    线程池用于完成任务队列中的所有任务
    """
    def __init__(self, num_threads):
        self.tasks = queue.Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kwargs):
        """ 添加任务至队列 """
        self.tasks.put((func, args, kwargs))

    def map(self, func, args_list):
        """ 添加一系列任务至队列 """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ 等待队列中所有任务完成 """
        self.tasks.join()


def storage(path=OUT_PATH, stock_list=None, start='2006-01-01', end='2007-01-01',
            data_type='tick', flag='init', auto=True):
    """
    存储，目前仅支持'HDF5'
    参数：
    - path (str): 文件存储路径
    - stock_list (list): 需要存储的股票列表
    - start (str): 开始日期，格式为'YYYY-MM-DD'
    - end (str): 结束日期
    - data_type (str): 市场行情数据类型
    - flag (str): 'init'为初始化，或'update'更新数据
    - auto (bool): 如果start不是最新的，update模式下自动加1
    """
    if stock_list is None:
        try:
            with open(os.path.join(path, STORAGE['STOCK_FILE']), 'rb') as fp:
                stock_list = pickle.load(fp)
        except Exception:
            stock_info = get_stock_info()
            stock_list = stock_info['stock_list']

            if not os.path.isfile(os.path.join(OUT_PATH, STORAGE['STOCK_FILE'])):
                with open(os.path.join(OUT_PATH, STORAGE['STOCK_FILE']), 'wb') as fp:
                    pickle.dump(stock_list, fp)

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    dt_list = [dt.strftime("%Y-%m-%d") for dt in pd.date_range(start=start_dt, end=end_dt, freq='D')]

    # 1 # tick数据，symbol文件中的以日期为key
    def ticks_of_stock(symbol):
        filename = os.path.join(path, STORAGE['Tick'], symbol+'.h5')
        stock_dt_list = dt_list
        if flag == 'update':
            nearest_dt = pd.to_datetime(sorted(hdf_keys(filename, clean=True))[-1])
            if nearest_dt >= start_dt:
                if auto:
                    new_start_dt = nearest_dt + datetime.timedelta(days=1)
                    stock_dt_list = [dt.strftime("%Y-%m-%d") for dt in pd.date_range(start=new_start_dt,
                                                                                     end=end_dt, freq='B')]
                    print('Warning: the start date has been changed to %s' % nearest_dt)
                else:
                    print('Error: already includes is %s, abort update %s!' % (nearest_dt, symbol))
                    return
        for dt in stock_dt_list:
            ticks = get_ticks_tushare(symbol, dt)
            if  ticks is not None:
                ticks.to_hdf(filename, dt, format='table', append=False)
                print('Save', symbol, 'at', dt, 'Done!')

    # 2 # 后复权因子数据，factor文件中以stock为key
    def auth_factor(symbol):
        new_start = start
        if flag == 'update':
            nearest_dt = pd.read_hdf(factor_filename, key=symbol).index[-1]
            if nearest_dt >= start_dt:
                if auto:
                    new_start = (nearest_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    print('Warning: the start date has been changed to %s' % nearest_dt)
                else:
                    print('Error: already includes is %s, abort update %s!' % (nearest_dt, symbol))
                    return
        factors = get_auth_factor(symbol, start=new_start, end=end)
        factors.to_hdf(factor_filename, symbol, format='table', append=True)
        print('Save', symbol, 'Done!')

    ###### 多线程收集数据 ##########
    pool = ThreadPool(NUM_THREAD)

    if data_type == 'tick':
        pool.map(ticks_of_stock, stock_list)
    elif data_type == 'factor':
        factor_filename = os.path.join(path, STORAGE['Factor'], 'stock_factor.h5')
        pool.map(auth_factor, stock_list)
    pool.wait_completion()
