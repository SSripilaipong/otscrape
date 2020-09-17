from multiprocessing import Pool, Value, Event


class PoolWorkersBase:
    def __init__(self, n_workers):
        assert n_workers > 0

        self.n_workers = n_workers

        self.ready = False
        self.workers = None  # type: Pool

        self._remain_tasks = None
        self._work_done_event = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def open(self):
        assert not self.ready

        self._remain_tasks = Value('i', 0)
        self._work_done_event = Event()
        self.workers = Pool(self.n_workers)
        self.ready = True

        return self

    def close(self):
        assert self.ready

        self._work_done_event.clear()
        while self.count_remaining_tasks() > 0:
            self._work_done_event.wait()
            self._work_done_event.clear()

        self.workers.close()
        self.workers.join()

    def count_remaining_tasks(self):
        with self._remain_tasks.get_lock():
            return self._remain_tasks.value

    def increase_task_counter(self):
        with self._remain_tasks.get_lock():
            self._remain_tasks.value += 1

    def decrease_task_counter(self):
        with self._remain_tasks.get_lock():
            self._remain_tasks.value -= 1

        self._work_done_event.set()


class PoolCommand:
    @staticmethod
    def calculate(page):
        raise NotImplementedError()

    def callback(self, x):
        raise NotImplementedError()

    def finish(self, pages, *args, **kwargs):
        raise NotImplementedError()
