from otscrape.core.base.loader import Loader


class DummyLoader(Loader):
    def __init__(self, data=None):
        self.data = data

    def __call__(self, data=None):
        data = data or self.data
        return data
