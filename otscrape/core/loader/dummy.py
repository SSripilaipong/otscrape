from otscrape.core.base.loader import Loader


class DummyLoader(Loader):
    def __init__(self, data=None, rate_limit=''):
        super().__init__(rate_limit=rate_limit)

        self.data = data

    def do_load(self, data=None):
        data = self.data if data is None else data
        return data
