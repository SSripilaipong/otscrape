from typing import List, Callable, Union
from collections.abc import Iterable

from otscrape.core.base.extractor import Extractor
from .lambda_ import Lambda, StarLambda
from .chain import Chain


class MapBase(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.func = func
        self.lambda_replace_error = replace_error

        if isinstance(self.func, Extractor):
            self.lambda_ = self.func
        else:
            self.lambda_ = self._get_lambda()

    @property
    def _get_lambda(self):
        raise NotImplementedError()

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (Iterable,))

        return [self.lambda_({self.lambda_.target: e}) for e in x]


class Map(MapBase):
    def _get_lambda(self):
        return Lambda(self.func, replace_error=self.lambda_replace_error)

    def __str__(self):
        return f'Map({self.func.__name__})'


class StarMap(MapBase):
    def _get_lambda(self):
        return StarLambda(self.func, replace_error=self.lambda_replace_error)

    def __str__(self):
        return f'StarMap({self.func.__name__})'


class ChainMap(Map):
    def __init__(self, extractors: List[Union[Extractor, Callable]], *, target=None, project=True):
        func = Chain(extractors)

        super().__init__(func, target=target, project=project)

    def __str__(self):
        return f'ChainMap({self.func.__name__})'
