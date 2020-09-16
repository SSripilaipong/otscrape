import time

from otscrape.core.base.data_model import DataModel
from otscrape.core.base.attribute import attribute
from otscrape.core.base.loader import Loader


class Page(DataModel):
    def __init__(self, **kwargs):
        super().__init__()

        self._loader_kwargs = kwargs
        self.cached = {}
        self._raw = None

    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def loader(self) -> Loader:
        raise NotImplementedError()

    @attribute(project=False)
    def raw(self):
        if self._raw is None:
            self.fetch()
        return self._raw

    def fetch(self):
        wait_time = self.loader.get_available_time()

        while True:
            time.sleep(wait_time)

            try:
                self.loader.do_on_loading()
                break
            except AssertionError:
                wait_time = self.loader.get_available_time()
                continue

        self.do_load()

    def do_load(self):
        self._raw = self.loader.do_load(**self._loader_kwargs)
