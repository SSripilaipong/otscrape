from otscrape.core.base.page import Page
from otscrape.core.base.worker import PoolCommand
from otscrape.core.base.exporter import Exporter


class ExportCommand(PoolCommand):
    def __init__(self, exporter: Exporter):
        super().__init__()

        self.exporter = exporter

    @staticmethod
    def calculate(page: Page):
        page.do_load()
        return page.get_data()

    def callback(self, x):
        self.exporter(x)

    def finish(self, pages, *args, **kwargs):
        return
