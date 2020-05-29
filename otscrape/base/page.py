from otscrape.base.data_model import DataModel, attribute
from otscrape.base.loader import Loader


class Page(DataModel):

    @property
    def loader(self) -> Loader:
        raise NotImplementedError()

    def get_loader_params(self) -> dict:
        raise NotImplementedError()

    @attribute
    def raw(self):
        return self.loader.load(**self.get_loader_params())
