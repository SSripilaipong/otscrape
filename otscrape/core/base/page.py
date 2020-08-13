from typing import Callable

from otscrape.core.base.data_model import DataModel
from otscrape.core.base.attribute import attribute


class Page(DataModel):
    def __init__(self, **kwargs):
        super().__init__()

        self._loader_kwargs = kwargs
        self.cached = {}

    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def loader(self) -> Callable:
        raise NotImplementedError()

    @attribute(project=False)
    def raw(self):
        return self.fetch()

    def fetch(self):
        return self.loader(**self._loader_kwargs)
