from abc import ABC
from threading import Thread, Lock
from queue import Queue, Empty

from .abstract import WillFail, NoFailMixin

from otscrape.core.util import ensure_dict


class ExporterBase(WillFail):
    def __init__(self):
        self.ready = False

    def on_open(self):
        pass

    def on_close(self):
        pass

    def open(self):
        self.on_open()
        self.ready = True

    def export(self, data):
        raise NotImplementedError()

    def close(self):
        self.ready = False
        self.on_close()

    def _run(self, page):
        data = ensure_dict(page)
        self.export(data)

    def __call__(self, page):
        assert self.ready

        self._run_will_fail(page)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class ParallelizableExporterBase(ABC, ExporterBase):
    def __init__(self, queue_size=0, queue_timeout=3, parallel=False):
        super().__init__()

        self.queue_size = queue_size
        self.queue_timeout = queue_timeout
        self.parallel = parallel

        self.ready_lock = Lock()
        self.worker = None
        self.page_queue = None

    def _run(self, page):
        try:
            super()._run(page)
        finally:
            if self.parallel:
                self.page_queue.task_done()

    def _worker_loop(self):
        super().open()

        while self.ready:
            try:
                page = self.page_queue.get(timeout=self.queue_timeout)
            except Empty:
                continue

            self._run_will_fail(page)

        super().close()

    def __call__(self, page):
        assert self.ready

        if self.parallel:
            self.page_queue.put(page)
        else:
            super().__call__(page)

    def open(self):
        assert not self.ready

        if self.parallel:
            self.page_queue = Queue(maxsize=self.queue_size)

            self.worker = Thread(target=self._worker_loop)
            self.worker.start()
            while not self.ready:
                pass
            return self
        else:
            return super().open()

    def close(self):
        assert self.ready

        if self.parallel:
            self.join_queue()

            self.ready = False
            self.join_worker()

            self.page_queue = None
        else:
            super().close()

    def join_queue(self):
        self.page_queue.join()

    def join_worker(self):
        self.worker.join()


class Exporter(NoFailMixin, ParallelizableExporterBase):

    def on_error(self, *args, **kwargs):
        message = f'An error occurred while exporting using {self.__class__.__name__}.'
        super().on_error(*args, message=message, **kwargs)
