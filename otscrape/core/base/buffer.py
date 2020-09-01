from threading import Lock


class BufferRetryException(Exception):
    pass


class Buffer:
    def __init__(self, buffer_size=0, buffer_timeout=None, total_tasks=None):
        self.buffer_size = buffer_size
        self.buffer_timeout = buffer_timeout
        self.total_tasks = total_tasks

        self._task_count = 0
        self._counter_lock = Lock()

    @property
    def task_count(self):
        with self._counter_lock:
            return self._task_count

    def increase_task_counter(self):
        with self._counter_lock:
            self._task_count += 1

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

    def put(self, x):
        raise NotImplementedError()

    def task_done(self):
        pass

    def __iter__(self):
        while not self.empty() or self.count_remaining_tasks():
            try:
                page = self.get()
            except BufferRetryException:
                continue

            data = page.get_data()
            self.task_done()
            yield data
