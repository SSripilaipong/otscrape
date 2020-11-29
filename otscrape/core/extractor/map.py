from collections.abc import Iterable
from otscrape import Extractor


class Map(Extractor):
    def __init__(self, func, target=None, project=True):
        super().__init__(target=target, project=project)
        self.func = func

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.func(e) for e in x]

    def __str__(self):
        return f'Map({self.func.__name__})'
