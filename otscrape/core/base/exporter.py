from abc import ABC
from threading import Thread, Lock
from queue import Queue, Empty

from .mixins import NoFailMixin
from .page import Page


def ensure_dict(page):
    if isinstance(page, Page):
        data = page.get_data()
    elif isinstance(page, dict):
        data = page
    else:
        raise TypeError(f'type {type(page)} is not supported')

    return data


class ExporterBase:
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

    def _process(self, page):
        try:
            data = ensure_dict(page)
            self.export(data)
        except Exception as e:
            self.on_export_error(e)

    def on_export_error(self, exception):
        pass

    def __call__(self, page):
        assert self.ready

        self._process(page)

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

    def _process(self, page):
        try:
            super()._process(page)
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

            self._process(page)

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

    def on_export_error(self, *args, **kwargs):
        message = f'An error occurred while exporting using {self.__class__.__name__}.'
        self.on_error(*args, message=message, **kwargs)
