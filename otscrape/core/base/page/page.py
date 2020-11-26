import time

from otscrape.core.base.data_model import DataModel
from otscrape.core.base.extractor import extractor
from otscrape.core.base.loader import Loader


class PageBase(DataModel):
    def __init__(self, **kwargs):
        super().__init__()

        self._loader_kwargs = kwargs
        self._cached = {}
        self._raw = None
        self._is_loaded = False

    @property
    def loader(self) -> Loader:
        raise NotImplementedError()

    @extractor(project=False)
    def raw(self):
        if self._is_loaded:
            return self._raw

        return self.fetch()

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

        return self.do_load()

    def do_load(self):
        self._raw = self.loader.do_load(**self._loader_kwargs)
        self._attr_cached['raw'] = self._raw
        self._is_loaded = True
        return self._raw

    def prune(self):
        cache_result = {}

        attrs = self._project_attrs | {'raw'}
        if 'key' in self._attrs:
            attrs.add('key')

        for attr in attrs:
            self._cached = {}
            cache_result[attr] = self._attr_cached[attr]

        self._attr_cached = cache_result
