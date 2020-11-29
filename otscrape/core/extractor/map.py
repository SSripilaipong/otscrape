from collections.abc import Iterable
from otscrape import Extractor


class MapperExtractor(Extractor):
    def __init__(self, func, target=None, project=True):
        super().__init__(target=target, project=project)
        self.func = func

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.func(e) for e in x]

    def __str__(self):
        return f'MapperExtractor({self.func.__name__})'


def map(func, target=None, project=True):
    return MapperExtractor(func, target=target, project=project)
