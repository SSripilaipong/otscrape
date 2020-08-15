from threading import Thread
from queue import Queue


class ThreadWorkersBase:
    def __init__(self, n_workers, queue_size=0, queue_timeout=3):
        assert n_workers > 0

        self.n_workers = n_workers
        self.queue_size = queue_size
        self.queue_timeout = queue_timeout

        self.ready = False
        self.workers = []
        self.queue = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _worker_loop(self):
        while self.ready:
            try:
                method, kwargs = self.queue.get(timeout=self.queue_timeout)
                method(**kwargs)
            except:
                pass
            finally:
                self.queue.task_done()

    def open(self):
        assert not self.ready

        self.queue = Queue(maxsize=self.queue_size)
        self.ready = True

        self.workers = [Thread(target=self._worker_loop) for _ in range(self.n_workers)]
        for w in self.workers:
            w.start()

        return self

    def close(self):
        assert self.ready
        self.queue.join()

        self.ready = False
        for w in self.workers:
            w.join()

        self.queue = None

    def iter_results(self):
        pass


Workers = ThreadWorkersBase
