import os
from threading import Thread
import threading
import queue
from multiprocessing import JoinableQueue, cpu_count, Lock, Value

from otscrape.core.base.exception import DropCommandException
from otscrape.core.base.loader import Loader


class LineFetcher(Thread):
    def __init__(self, filename, data_queue: JoinableQueue, fetch_size, params=None):
        super().__init__()

        self.filename = filename
        self.data_queue = data_queue
        self.fetch_size = fetch_size

        _params = {'mode': 'r'}
        _params.update(params)
        self.file = open(filename, **_params)
        self.st_size = os.fstat(self.file.fileno()).st_size
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
        line = self.file.readline()
        with self._n_lines_lock:
            self._n_lines += 1

        if self.file.tell() == self.st_size:
            self._is_eof = True

        return line

    def run(self):
        while not self.is_finished:
            n_fill = self.fetch_size - self.data_queue.qsize()
            for _ in range(n_fill):
                if self._is_eof or self.is_finished:
                    break
                self.data_queue.put(self.fetch_one_line())

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

        self.file.close()


class LineObject:
    def __init__(self, filename, line_no, content):
        self.content = content
        self.filename = filename
        self.line_no = line_no

    def __repr__(self):
        n_char = 20
        content = self.content if len(self.content) < n_char else f'{self.content[:n_char]}...'
        return f'LineObject({self.filename!r}, {self.line_no}, {content!r})'


class LineLoader(Loader):
    def __init__(self, filename, rate_limit='', fetch_size=None, **kwargs):
        super().__init__(rate_limit=rate_limit)

        self.filename = filename
        self.fetch_size = fetch_size or (cpu_count() * 2)
        self.kwargs = kwargs

        self.line_no = Value('L', 0)
        self.line_queue = JoinableQueue()
        self.fetcher = self.get_fetcher()
        self.fetcher.start()

        self._count_load = 0

    def get_fetcher(self):
        return LineFetcher(self.filename, self.line_queue, self.fetch_size, self.kwargs)

    def has_more_lines(self):
        return not self.fetcher.is_finished

    def reset(self):
        self.fetcher.close()
        self.fetcher.join()

        self.line_queue.close()
        self.line_queue = JoinableQueue()

        self.line_no = Value('L', 0)
        self.fetcher = self.get_fetcher()
        self.fetcher.start()

    def on_loading(self):
        super().on_loading()

        if self.fetcher.is_finished and self._count_load >= self.fetcher.n_lines:
            raise DropCommandException()

        self._count_load += 1

    def do_load(self):
        while True:
            try:
                content = self.line_queue.get(timeout=3)

                with self.line_no.get_lock():
                    data = LineObject(self.filename, self.line_no.value, content)
                    self.line_no.value += 1

                self.line_queue.task_done()
                return data

            except queue.Empty:
                if not self.has_more_lines():
                    raise DropCommandException('All lines are already read.')
