from requests import Response

from otscrape.core.base.extractor import Extractor

from .request import RequestText
from .text.soup import TextSoup


class Soup(TextSoup):
    def __init__(self, target=None, *, project=True, replace_error=None, **kwargs):
        super().__init__(target, project=project, replace_error=replace_error, **kwargs)

        self._req_parser = RequestText(target=self.target)

    def extract(self, page, cache):
        target = self.target
        x = page[target]
        cache_name = f'{target}#Soup'

        if cache_name in cache:
            soup = cache[cache_name]
        else:
            if isinstance(x, Response):
                x = self._req_parser.extract(page, cache)

            if isinstance(x, (str, bytes)):
                soup = super().extract({self.target: x}, cache)
                cache[cache_name] = soup

            else:
                raise TypeError(f'Unexpected type {x.__class__.__name__} for a Soup extractor.')

        return soup


class SoupFindAll(Extractor):
    def __init__(self, name=None, attrs={}, recursive=True, string=None, limit=None, *,
                 target=None, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        kwargs.update({'name': name, 'attrs': attrs, 'recursive': recursive,
                       'string': string, 'limit': limit})
        self.kwargs = kwargs

        self._soup_ext = Soup(self.target)

    def extract(self, page, cache):
        soup = self._soup_ext.extract(page, cache)

        return soup.find_all(**self.kwargs)
