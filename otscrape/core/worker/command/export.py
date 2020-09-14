from otscrape.core.base.worker import PoolWorkersBase, PoolCommand
from otscrape.core.base.exporter import Exporter


class ExportCommand(PoolCommand):
    def __init__(self, pool: PoolWorkersBase, exporter: Exporter):
        super().__init__(pool)

        self.exporter = exporter

    @staticmethod
    def calculate(page):
        return page.get_data()

    def callback(self, x):
        self.exporter(x)

    def finish(self, pages, *args, **kwargs):
        return
