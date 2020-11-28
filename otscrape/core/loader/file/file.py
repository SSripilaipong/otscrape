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
from .reader import LineReader


class TextFileLineReader(LineReader):
    def __init__(self, filename, skiprows=0, **params):
        super().__init__(skiprows=skiprows)

        self.filename = filename

        self.params = {'mode': 'r'}
        self.params.update(params or {})

        self.file = None
        self.st_size = None

    def _open(self):
        self.file = open(self.filename, **self.params)
        self.st_size = os.fstat(self.file.fileno()).st_size

    def close(self):
        self.file.close()

    def is_eof(self):
        return self.file.tell() == self.st_size

    def read_line(self):
        return self.file.readline()


class FilesManager:
    def __init__(self, readers):
        self.readers = deque(readers)

        self.n_lines = 0
        self.is_eof = False

        for reader in self.readers:
            reader.open()

    def fetch_one_line(self):
        reader = self.readers[0]
        filename = reader.filename

        try:
            line = reader.read_line()
        except StopIteration as e:
            self.reach_file_eof()
            raise e

        line_no = self.n_lines
        self.n_lines += 1

        if reader.is_eof():
            self.reach_file_eof()

        obj = LineObject(filename, line_no, line)
        return obj

    def reach_file_eof(self):
        self.readers.popleft()

        if not self.readers:
            self.is_eof = True
        else:
            self.n_lines = 0

    def close(self):
        for reader in self.readers:
            reader.close()


class LineFetcher(Thread):
    def __init__(self, manager, data_queue: JoinableQueue, fetch_size):
        super().__init__()

        self.manager = manager
        self.data_queue = data_queue
        self.fetch_size = fetch_size

        self.lock = Lock()
        self._is_finished = Value('B', 0)

        self._n_lines_lock = threading.Lock()

    @property
    def n_lines(self):
        with self._n_lines_lock:
            return self.manager.n_lines

    @property
    def is_finished(self):
        with self._is_finished.get_lock():
            return bool(self._is_finished.value)

    def fetch_one_line(self):
        with self._n_lines_lock:
            return self.manager.fetch_one_line()

    @property
    def is_eof(self):
        return self.manager.is_eof

    def run(self):
        while not self.is_finished:
            n_fill = self.fetch_size - self.data_queue.qsize()
            for _ in range(n_fill):
                if self.is_eof or self.is_finished:
                    break

                try:
                    obj = self.fetch_one_line()
                    self.data_queue.put(obj)
                except StopIteration:
                    break

            if self.is_eof or self.is_finished:
                break

            self.data_queue.join()
            if self.is_eof:
                break

        with self._is_finished.get_lock():
            self._is_finished.value = 1

    def close(self):
        with self._is_finished.get_lock():
            self._is_finished.value = 1

        while self.data_queue.qsize() > 0:
            self.data_queue.get(timeout=3)
            self.data_queue.task_done()

        self.manager.close()


class LineLoader(Loader):
    def __init__(self, filenames=None, rate_limit='', fetch_size=None, skiprows=0, parallel=False, **kwargs):
        super().__init__(rate_limit=rate_limit)

        if filenames is None:
            return
        if isinstance(filenames, Iterable) and not isinstance(filenames, str):
            self.filenames = filenames
        else:
            self.filenames = [filenames]

        self.parallel = parallel
        self.kwargs = kwargs
        self.skiprows = skiprows

        self._count_load = 0
        self.tot_line = self.calculate_tot_line() - self.skiprows * len(self.filenames)

        if parallel:
            self.manager = None
            self.fetch_size = fetch_size or (cpu_count() * 2)
            self.line_queue = JoinableQueue()
            self.fetcher = self.get_fetcher()

            self.fetcher.start()
        else:
            self.manager = self.get_manager()
            self.fetch_size = None
            self.line_queue = None
            self.fetcher = None

    def __getstate__(self):
        state = super().__getstate__()
        del state['fetcher']
        return state

    def __setstate__(self, state):
        super().__setstate__(state)
        self.__dict__['fetcher'] = None

    def get_manager(self):
        readers = [self.get_line_reader(filename) for filename in self.filenames]
        return FilesManager(readers)

    def get_fetcher(self):
        manager = self.get_manager()
        return LineFetcher(manager, self.line_queue, self.fetch_size)

    def get_line_reader(self, filename):
        return TextFileLineReader(filename, skiprows=self.skiprows, **self.kwargs)

    def calculate_tot_line(self):
        return sum(1 for filename in self.filenames for _ in open(filename, **self.kwargs))

    def reset(self):
        self._count_load = 0
        self.tot_line = self.calculate_tot_line() - self.skiprows * len(self.filenames)

        if self.parallel:
            self.fetcher.close()
            self.fetcher.join()

            self.line_queue.close()
            self.line_queue = JoinableQueue()

            self.fetcher = self.get_fetcher()
            self.fetcher.start()
        else:
            self.manager.close()
            self.manager = self.get_manager()

    def on_loading(self):
        super().on_loading()

        if self._count_load >= self.tot_line:
            raise DropCommandException()

        self._count_load += 1

    def _do_load_nonparallel(self):
        return self.manager.fetch_one_line()

    def _do_load_parallel(self):
        while True:
            try:
                data = self.line_queue.get(timeout=3)

                self.line_queue.task_done()
                return data

            except queue.Empty:
                if self.fetcher.is_finished:
                    break

    def do_load(self):
        if self.parallel:
            return self._do_load_parallel()
        else:
            return self._do_load_nonparallel()
