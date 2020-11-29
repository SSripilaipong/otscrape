from collections.abc import Iterable

from otscrape.core.base.extractor import Extractor
from .lambda_ import Lambda, StarLambda


class Map(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.func = func

        if isinstance(self.func, Extractor):
            self.lambda_ = self.func
        else:
            self.lambda_ = Lambda(self.func, replace_error=replace_error)

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.lambda_({self.lambda_.target: e}) for e in x]

    def __str__(self):
        return f'Map({self.func.__name__})'


class StarMap(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.func = func

        if isinstance(self.func, Extractor):
            self.lambda_ = self.func
        else:
            self.lambda_ = StarLambda(self.func, replace_error=replace_error)

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.lambda_({self.lambda_.target: e}) for e in x]

    def __str__(self):
        return f'StarMap({self.func.__name__})'
