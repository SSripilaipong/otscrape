import multiprocessing
from multiprocessing import Pool, Value, Event


def ensure_n_workers(n_workers):
    if n_workers == -1 or n_workers is None:
        n_workers = multiprocessing.cpu_count()
    else:
        assert 0 < n_workers < multiprocessing.cpu_count()
    return n_workers


class PoolManager:
    def __init__(self, n_workers=None):
        self.n_workers = ensure_n_workers(n_workers)

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

    def close(self, force=False):
        assert self.ready

        if not force:
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
    def prepare(page):
        page.loader.do_on_loading()

    def validate_input(self, page):
        return

    @staticmethod
    def calculate(page):
        raise NotImplementedError()

    def callback(self, x):
        return

    def finish(self, pages, *args, **kwargs):
        return

    def create_task(self, page):
        task = PoolTask(self, page)
        return task


class PoolTask:
    def __init__(self, command: PoolCommand, page):
        self.command = command
        self.page = page

        self.command.validate_input(self.page)

        self.calculation = command.calculate
        self.callback = command.callback

    def prepare(self):
        return self.command.prepare(self.page)
