from threading import Thread, Lock
from queue import Queue, Empty


class ThreadWorkersBase:
    def __init__(self, n_workers, queue_size=0, queue_timeout=3):
        assert n_workers > 0

        self.n_workers = n_workers
        self.queue_size = queue_size
        self.queue_timeout = queue_timeout

        self.ready = False
        self.workers = []
        self.queue = None

        self._available_workers = 0
        self.aw_lock = Lock()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def count_available_workers(self):
        with self.aw_lock:
            return self._available_workers

    def _worker_loop(self):
        while self.ready:
            try:
                method, kwargs = self.queue.get(timeout=self.queue_timeout)
            except Empty:
                continue

            try:
                with self.aw_lock:
                    self._available_workers -= 1
                method(**kwargs)
            except:
                pass
            finally:
                self.queue.task_done()
                with self.aw_lock:
                    self._available_workers += 1

    def open(self):
        assert not self.ready

        self.queue = Queue(maxsize=self.queue_size)
        self.ready = True
        self._available_workers = self.n_workers

        self.workers = [Thread(target=self._worker_loop) for _ in range(self.n_workers)]
        for w in self.workers:
            w.start()

        return self

    def close(self):
        assert self.ready
        self.queue.join()

        self.ready = False
        self._available_workers = 0
        for w in self.workers:
            w.join()

        self.queue = None
        self.workers = []

    def count_active_workers(self):
        return sum(w.is_alive() for w in self.workers)

