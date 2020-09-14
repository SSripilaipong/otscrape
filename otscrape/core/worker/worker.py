from otscrape.core.base.worker import PoolWorkersBase
from .command import ScrapeCommand, ExportCommand


class Workers(PoolWorkersBase):
    def __init__(self, n_workers):
        super().__init__(n_workers=n_workers)

    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        command = ScrapeCommand(self, buffer, buffer_size, buffer_timeout)
        return command.apply(page)

    def export(self, page, exporter):
        command = ExportCommand(self, exporter)
        return command.apply(page)
