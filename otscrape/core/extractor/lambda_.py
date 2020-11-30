from collections.abc import Iterable

from otscrape.core.base.data_model import DataModel
from otscrape.core.base.extractor import Extractor


class Lambda(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)
        self.func = func

    def extract(self, page, cache):
        x = page[self.target]
        return self.func(x)

    def __str__(self):
        return f'Lambda({self.func.__name__})'


class StarLambda(Extractor):
    def __init__(self, func, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)
        self.func = func

    def extract(self, page, cache):
        x = page[self.target]
        args, kwargs = [], {}

        if isinstance(x, DataModel):
            args = x.get_data()
        elif isinstance(x, dict):
            kwargs = dict(x)
        elif isinstance(x, Iterable):
            args = list(x)

        return self.func(*args, **kwargs)

    def __str__(self):
        return f'StarLambda({self.func.__name__})'
