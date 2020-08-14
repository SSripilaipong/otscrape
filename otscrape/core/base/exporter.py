from threading import Thread
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
    def __init__(self, queue_size=0, queue_timeout=3, parallel=False):
        self.queue_size = queue_size
        self.queue_timeout = queue_timeout
        self.parallel = parallel

        self.ready = False
        self.worker = None
        self.page_queue = None

    def _open(self):
        self.open()
        self.ready = True

    def _close(self):
        self.ready = False
        self.close()

    def open(self):
        pass

    def export(self, data):
        raise NotImplementedError()

    def close(self):
        pass

    def _process(self, page):
        try:
            data = ensure_dict(page)
            self.export(data)
        except Exception as e:
            self.on_export_error(e)
        finally:
            if self.parallel:
                self.page_queue.task_done()

    def _worker_loop(self):
        self._open()

        while self.ready:
            try:
                page = self.page_queue.get(timeout=self.queue_timeout)
            except Empty:
                continue

            self._process(page)

        self._close()

    def on_export_error(self, exception):
        pass

    def __call__(self, page):
        assert self.ready

        if self.parallel:
            self.page_queue.put(page)
        else:
            self._process(page)

    def __enter__(self):
        if self.parallel:
            self.page_queue = Queue(maxsize=self.queue_size)

            self.worker = Thread(target=self._worker_loop)
            self.worker.start()
            while not self.ready:
                pass
        else:
            self._open()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.parallel:
            self.join_queue()

            self.ready = False
            self.join_worker()

            self.page_queue = None
        else:
            self._close()

    def join_queue(self):
        self.page_queue.join()

    def join_worker(self):
        self.worker.join()


class Exporter(NoFailMixin, ExporterBase):

    def on_export_error(self, *args, **kwargs):
        message = f'An error occurred while exporting using {self.__class__.__name__}.'
        self.on_error(*args, message=message, **kwargs)
