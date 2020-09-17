from otscrape.core.base.worker import CommandExecutor

from .command import ScrapeCommand, ExportCommand


class Workers:
    def __init__(self, n_workers):
        self._exporter_cache = {}
        self._executor = CommandExecutor(n_workers)

    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        command = ScrapeCommand(buffer, buffer_size, buffer_timeout)
        return self._executor.execute(command, page)

    def export(self, page, exporter, **kwargs):
        command = ExportCommand(exporter, self._exporter_cache, **kwargs)
        return self._executor.execute(command, page)

    def open(self):
        self._executor.open()
        self._exporter_cache = {}
        return self

    def close(self):
        self._executor.close()

        for exporter in self._exporter_cache.values():
            exporter.close()
        self._exporter_cache = {}

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
