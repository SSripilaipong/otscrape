from otscrape.core.base.worker import PoolWorkersBase

from .command import ScrapeCommand, ExportCommand
from .executor import CommandExecutor


class Workers(PoolWorkersBase):
    def __init__(self, n_workers):
        super().__init__(n_workers=n_workers)

        self._exporter_cache = {}
        self._executor = CommandExecutor(self)

    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        command = ScrapeCommand(buffer, buffer_size, buffer_timeout)
        return self._executor.execute(command, page)

    def export(self, page, exporter, **kwargs):
        command = ExportCommand(exporter, self._exporter_cache, **kwargs)
        return self._executor.execute(command, page)

    def open(self):
        r = super().open()
        self._exporter_cache = {}
        return r

    def close(self):
        super().close()

        for exporter in self._exporter_cache.values():
            exporter.close()

        self._exporter_cache = {}
