import time
from threading import Lock

from otscrape.core.base.wrapper import PageWrapper


class BufferRetryException(Exception):
    pass


class Buffer:
    def __init__(self, workers, buffer_size=0, buffer_timeout=None, total_tasks=None):
        self.workers = workers
        self.buffer_size = buffer_size
        self.buffer_timeout = buffer_timeout
        self.total_tasks = total_tasks

        self._task_count = 0
        self._counter_lock = Lock()

    @property
    def task_count(self):
        with self._counter_lock:
            return self._task_count

    @task_count.setter
    def task_count(self, value):
        with self._counter_lock:
            self._task_count = value

    def increase_task_counter(self):
        with self._counter_lock:
            self._task_count += 1

    def decrease_task_counter(self):
        with self._counter_lock:
            self._task_count -= 1

    def count_remaining_tasks(self):
        if self.total_tasks is not None:
            count = self.task_count

            if count <= self.total_tasks:
                return self.total_tasks - count
            else:
                raise ValueError(f'The number of tasks done should not be higher than the total number of tasks. '
                                 f'({count} > {self.total_tasks})')
        else:
            return float('inf')

    def empty(self):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def put(self, x: PageWrapper):
        raise NotImplementedError()

    def task_done(self):
        pass

    @staticmethod
    def _iter_filter(obj):
        return not obj.exception

    def _iter(self):
        while not self.empty() or self.count_remaining_tasks():
            while not self.empty() or self.count_remaining_tasks():
                try:
                    obj = self.get()
                except BufferRetryException:
                    continue

                self.task_done()

                if self._iter_filter(obj):
                    yield obj

            time.sleep(0.1)

    def __iter__(self):
        if not self.workers.current_state:
            for obj in self._iter():
                yield obj.page
            return

        for obj in self.workers.iter(self._iter(), key=lambda o: o.page):
            page = obj.page
            state = obj.state

            ss = self.workers.current_state
            state.wait_for(ss)

            yield page
