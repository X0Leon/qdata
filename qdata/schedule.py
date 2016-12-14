# -*- coding: utf-8 -*-

"""
数据获取、存储的中心调度模块

@author: X0Leon
@version: 0.1
"""

try:
    import queue
except ImportError:
    import Queue as queue

import os
import datetime
import pickle
from threading import Thread
import warnings
warnings.filterwarnings('ignore')

import  pandas as pd
from pandas.io.pytables import HDFStore

from .logger import setup_logger
from .config import NUM_THREADERS, OUT_PATH, STORAGE
from .fetch import get_bars, get_stock_info
from .storage import HDFStorage

logger = setup_logger()


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
                logger.error(e)
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


def init_storage():
    """
    初始化存储系统，目前仅支持‘hdf5'
    """
    try:
        stock_info = get_stock_info()
        stock_list = stock_info['stock_list']
        to_market = stock_info['to_market']
    except Exception:
        with open(os.path.join(OUT_PATH, STORAGE['STOCK_FILE']), 'rb') as fp:
            stock_list = pickle.load(fp)
        with open(os.path.join(OUT_PATH, STORAGE['TO_MARKET_FILE']), 'rb') as fp:
            to_market = pickle.load(fp)

    data_list = []
    saved_list = []

    def bars_list(symbol):
        time_int = to_market.loc[symbol, 'timeToMarket']
        if len(str(time_int)) == 8:
            time_dt = datetime.datetime.strptime(str(time_int), '%Y%m%d')
            time_str = datetime.datetime.strftime(time_dt, '%Y-%m-%d')
        else:
            time_str = ''
        data_list.append(get_bars(symbol, start=time_str, end=''))
        logger.info(' '.join(['Fetch', symbol, 'Done!']))
        saved_list.append(symbol)

    pool = ThreadPool(NUM_THREADERS)
    pool.map(bars_list, stock_list)
    pool.wait_completion()

    for d in data_list:
        s = HDFStorage(d, os.path.join(OUT_PATH, 'daily.h5'))
        s.save()
        logger.info(' '.join(['Save', s.symbol, 'Done!']))

    # 保存更新信息
    with HDFStore(os.path.join(OUT_PATH, STORAGE['TO_FILE'])) as store:
        store['meta_info'] = pd.Series({'last_try': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                                        'status': 'success'})

    # 保存股票列表和上市日期
    if not os.path.isfile(os.path.join(OUT_PATH, STORAGE['STOCK_FILE'])):
        with open(os.path.join(OUT_PATH, STORAGE['STOCK_FILE']), 'wb') as fp:
            pickle.dump(stock_list, fp)

    if not os.path.isfile(os.path.join(OUT_PATH, STORAGE['TO_MARKET_FILE'])):
        with open(os.path.join(OUT_PATH, STORAGE['TO_MARKET_FILE']), 'wb') as fp:
            pickle.dump(to_market, fp)

    # 各种原因未更新保存的股票列表
    failed_list = sorted(list(set(stock_list) - set(saved_list)))
    logger.error('Failed %s stocks, check the failed.txt!' % len(failed_list))

    with open(os.path.join(OUT_PATH, 'failed.txt'), 'w') as f:
        for item in failed_list:
            f.write('{}\n'.format(item))


def sync_storage():
    """
    交易日同步存储系统中的数据
    """
    with HDFStore(os.path.join(OUT_PATH, STORAGE['TO_FILE'])) as store:
        last_try = datetime.datetime.strptime(store['meta_info']['last_try'], '%Y-%m-%d %H:%M')
        status = store['meta_info']['status']

    if last_try.date() == datetime.datetime.now().date() and status == 'success':
        logger.info('Already the latest data!')
        return

    if os.path.isfile(os.path.join(OUT_PATH, STORAGE['STOCK_FILE'])):
        with open(os.path.join(OUT_PATH, STORAGE['STOCK_FILE']), 'rb') as fp:
            stock_list = pickle.load(fp)
    else:
        stock_list = get_stock_info()['stock_list']

    data_list = []
    saved_list = []

    def bars_list(symbol):
        data_list.append(get_bars(symbol, start=(last_try.date()+datetime.timedelta(days=1)).strftime('%Y-%m-%d')))
        logger.info(' '.join(['Fetch', symbol, 'Done!']))

    pool = ThreadPool(NUM_THREADERS)
    pool.map(bars_list, stock_list)
    pool.wait_completion()

    for d in data_list:
        s = HDFStorage(d, os.path.join(OUT_PATH, STORAGE['TO_FILE']))
        s.save()
        logger.info(' '.join(['Save', s.symbol, 'Done!']))
        saved_list.append(s.symbol)

    with HDFStore(os.path.join(OUT_PATH, STORAGE['TO_FILE'])) as store:
        store['meta_info'] = pd.Series({'last_try': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                                        'status': 'success'})

    # 各种原因未更新保存的股票列表
    failed_list = sorted(list(set(stock_list) - set(saved_list)))
    logger.error('Failed %s stocks, check the failed.txt!' % len(failed_list))

    with open(os.path.join(OUT_PATH, 'failed.txt'), 'w') as f:
        for item in failed_list:
            f.write('{}\n'.format(item))
