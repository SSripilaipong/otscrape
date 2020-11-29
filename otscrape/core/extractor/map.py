from collections.abc import Iterable

from otscrape.core.base.extractor import Extractor
from .lambda_ import Lambda


class Map(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.func = func
        self.lambda_ = Lambda(self.func, replace_error=replace_error)

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.lambda_({'raw': e}) for e in x]

    def __str__(self):
        return f'Map({self.func.__name__})'
