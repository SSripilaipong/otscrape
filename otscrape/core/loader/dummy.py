from otscrape.core.base.loader import Loader


class DummyLoader(Loader):
    def __init__(self, data=None):
        self.data = data

    def do_load(self, data=None):
        data = data or self.data
        return data
