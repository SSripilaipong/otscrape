from multiprocessing import Pool, Value

from otscrape.core.util import ensure_page_iter


class PoolWorkersBase:
    def __init__(self, n_workers):
        assert n_workers > 0

        self.n_workers = n_workers

        self.ready = False
        self.workers = None  # type: Pool

        self._remain_tasks = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def open(self):
        assert not self.ready

        self._remain_tasks = Value('i', 0)
        self.workers = Pool(self.n_workers)
        self.ready = True

        return self

    def close(self):
        assert self.ready

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


class PoolCommand:
    def __init__(self, pool: PoolWorkersBase):
        self.pool = pool

    def apply(self, page, *args, **kwargs):
        self.pool.increase_task_counter()

        pages = ensure_page_iter(page)

        pages_ = []
        for page_ in pages:
            self.pool.workers.apply_async(self.calculate, args=(page_,), callback=self.callback)
            pages_.append(page_)

        return self.finish(pages_, *args, **kwargs)

    def _callback(self, x):
        self.callback(x)
        self.pool.decrease_task_counter()

    @staticmethod
    def calculate(page):
        raise NotImplementedError()

    def callback(self, x):
        raise NotImplementedError()

    def finish(self, pages, *args, **kwargs):
        raise NotImplementedError()
