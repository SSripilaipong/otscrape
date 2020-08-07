from typing import Callable

from otscrape.base.data_model import DataModel, attribute


class Page(DataModel):
    def __init__(self, **kwargs):
        super().__init__()

        self._loader_kwargs = kwargs

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

    def __getitem__(self, name):
        if name not in self._attributes:
            raise ValueError(f'attribute {name} not found')

        return getattr(self, name)
