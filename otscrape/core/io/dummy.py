from otscrape.base import Loader


class DummyLoader(Loader):
    def __init__(self, data):
        self.data = data

    def load(self):
        return self.data
