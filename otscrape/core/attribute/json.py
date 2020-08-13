from requests import Response

from otscrape.core.base.attribute import Attribute

from .request import RequestJSON
from .text.json import JSONDict
from .dict import get_item_from_path


parsers = [
    (Response, RequestJSON),
    ((str, bytes), JSONDict),
]


class JSON(Attribute):
    def __init__(self, target=None, path='/', *, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.path = path
        self._kwargs = kwargs

        self._parsers = [(c, p(target, ** self._kwargs)) for c, p in parsers]

    def extract(self, page):
        target = self.target
        cache_name = f'{target}#JSON'

        if cache_name in page.cached:
            y = page.cached[cache_name]
        else:
            x = page[target]

            for c, p in self._parsers:
                if isinstance(x, c):
                    y = p.extract(page)
                    break
            else:
                raise TypeError(f'Unexpected type {x.__class__.__name__} for a JSON attribute.')

            page.cached[cache_name] = y

        item = get_item_from_path(y, self.path)
        return item
