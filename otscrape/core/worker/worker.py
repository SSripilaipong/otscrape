from queue import Queue

from otscrape.core.base.worker import ThreadWorkersBase


class Workers(ThreadWorkersBase):
    def __init__(self, n_workers, buffer_size=0, queue_size=0, queue_timeout=3):
        super().__init__(n_workers=n_workers, queue_size=queue_size, queue_timeout=queue_timeout)

        self.buffer_size = buffer_size  # type: int
        self.buffer = None

    def open(self):
        super().open()

        self.buffer = Queue(maxsize=self.buffer_size)
        return self

    def _scrape(self, page, exporter=None):
        page.fetch()
        if exporter:
            exporter(page)
        else:
            self.buffer.put(page)

    def scrape(self, page, exporter=None):
        self.queue.put((self._scrape, {'page': page, 'exporter': exporter}))

    def iter_results(self):
        while not self.buffer.empty() or not self.queue.empty() or self.count_available_workers() < self.n_workers:
            if self.buffer:
                yield self.buffer.get().get_data()
                self.buffer.task_done()
