import traceback
from multiprocessing.dummy import Pool
from threading import Lock


class ThreadWorkersBase:
    def __init__(self, n_workers):
        assert n_workers > 0

        self.n_workers = n_workers

        self.ready = False
        self.workers = None  # type: Pool

        self._remain_tasks = 0
        self._count_lock = Lock()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def count_remaining_tasks(self):
        with self._count_lock:
            return self._remain_tasks

    def _worker_call(self, method, kwargs, callback_always=None):
        try:
            method(**kwargs)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            e = e.__class__('An error occurred inside a worker.').with_traceback(e.__traceback__)
            traceback.print_exception(type(e), e, None)
        finally:
            if callback_always:
                callback_always()

            with self._count_lock:
                self._remain_tasks -= 1

    def open(self):
        assert not self.ready

        self._remain_tasks = 0
        self.workers = Pool(self.n_workers)
        self.ready = True

        return self

    def close(self):
        assert self.ready

        self.workers.close()
        self.workers.join()
