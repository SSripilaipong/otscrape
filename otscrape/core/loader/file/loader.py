import os
from typing import Iterable
from collections import deque
from threading import Thread
import threading
import queue
from multiprocessing import JoinableQueue, cpu_count, Lock, Value

from otscrape.core.base.exception import DropCommandException
from otscrape.core.base.loader import Loader

from .result import LineObject


class LineFetcher(Thread):
    def __init__(self, filenames, data_queue: JoinableQueue, fetch_size, params=None):
        super().__init__()

        self.filenames = deque(filenames)
        self.data_queue = data_queue
        self.fetch_size = fetch_size

        _params = {'mode': 'r'}
        _params.update(params)
        self.files = deque(open(filename, **_params) for filename in self.filenames)
        self.st_sizes = deque(os.fstat(file.fileno()).st_size for file in self.files)
        self.lock = Lock()
        self._is_eof = False
        self._is_finished = Value('B', 0)

        self._n_lines_lock = threading.Lock()
        self._n_lines = 0

    @property
    def n_lines(self):
        with self._n_lines_lock:
            return self._n_lines

    @property
    def is_finished(self):
        with self._is_finished.get_lock():
            return bool(self._is_finished.value)

    def fetch_one_line(self):
        filename = self.filenames[0]
        line = self.files[0].readline()
        with self._n_lines_lock:
            line_no = self._n_lines
            self._n_lines += 1

        if self.files[0].tell() == self.st_sizes[0]:
            self.filenames.popleft()
            self.files.popleft()
            self.st_sizes.popleft()

            if not self.files:
                assert not self.st_sizes
                self._is_eof = True
            else:
                with self._n_lines_lock:
                    self._n_lines = 0

        obj = LineObject(filename, line_no, line)
        return obj

    def run(self):
        while not self.is_finished:
            n_fill = self.fetch_size - self.data_queue.qsize()
            for _ in range(n_fill):
                if self._is_eof or self.is_finished:
                    break

                obj = self.fetch_one_line()
                self.data_queue.put(obj)

            if self._is_eof or self.is_finished:
                break

            self.data_queue.join()
            if self._is_eof:
                break

        with self._is_finished.get_lock():
            self._is_finished.value = 1

    def close(self):
        with self._is_finished.get_lock():
            self._is_finished.value = 1

        while self.data_queue.qsize() > 0:
            self.data_queue.get(timeout=3)
            self.data_queue.task_done()

        for file in self.files:
            file.close()


class LineLoader(Loader):
    def __init__(self, filenames=None, rate_limit='', fetch_size=None, **kwargs):
        super().__init__(rate_limit=rate_limit)

        if filenames is None:
            return
        if isinstance(filenames, Iterable) and not isinstance(filenames, str):
            self.filenames = filenames
        else:
            self.filenames = [filenames]

        self.fetch_size = fetch_size or (cpu_count() * 2)
        self.kwargs = kwargs

        self._count_load = 0
        self.tot_line = sum(1 for filename in self.filenames for _ in open(filename))

        self.line_queue = JoinableQueue()

        self.fetcher = self.get_fetcher()
        self.fetcher.start()

    def __getstate__(self):
        state = super().__getstate__()
        print()
        del state['fetcher']
        return state

    def __setstate__(self, state):
        super().__setstate__(state)
        self.__dict__['fetcher'] = None

    def get_fetcher(self):
        return LineFetcher(self.filenames, self.line_queue, self.fetch_size, self.kwargs)

    def reset(self):
        self._count_load = 0
        self.tot_line = sum(1 for filename in self.filenames for _ in open(filename))

        self.fetcher.close()
        self.fetcher.join()

        self.line_queue.close()
        self.line_queue = JoinableQueue()

        self.fetcher = self.get_fetcher()
        self.fetcher.start()

    def on_loading(self):
        super().on_loading()

        if self._count_load >= self.tot_line:
            raise DropCommandException()

        self._count_load += 1

    def do_load(self):
        while True:
            try:
                data = self.line_queue.get(timeout=3)

                self.line_queue.task_done()
                return data

            except queue.Empty:
                pass
