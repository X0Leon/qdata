# -*- coding: utf-8 -*-

# import sys
# IS_PY2 = sys.version_info < (3, 0)
# if IS_PY2:
#     from Queue import Queue
# else:
#     from queue import Queue

try:
    import queue
except ImportError:
    import Queue as queue

from threading import Thread


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
                print(e)
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


def init_hdf():
    pass

if __name__ == "__main__":
    from random import randrange
    from time import sleep

    # 在每个线程中执行的任务
    def wait_delay(d):
        print("sleeping for (%d)sec" % d)
        sleep(d)

    delays = [randrange(3, 7) for i in range(50)]

    # 实例化线程池，其中有5个工作的线程
    pool = ThreadPool(5)

    # 也可以用pool.add_task()添加单个任务
    pool.map(wait_delay, delays)
    pool.wait_completion()
