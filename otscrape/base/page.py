from otscrape.base.data_model import DataModel, attribute
from otscrape.base.loader import Loader


class Page(DataModel):
    def __init__(self, loader: Loader):
        super().__init__()

        self._loader = loader

    @attribute
    def raw(self):
        return self._loader.load()
