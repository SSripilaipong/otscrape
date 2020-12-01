from requests import Response

from otscrape.core.base.extractor import Extractor
from .text.etree import parse
from .request import RequestText


class XPath(Extractor):
    def __init__(self, xpath='.', *, target=None, only_first=False, encoding=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.xpath = xpath
        self.only_first = only_first
        self._req_parser = RequestText(target, encoding=encoding)

    def extract(self, page, cache):
        target = self.target
        x = page[target]

        if isinstance(x, Response):
            x = self._req_parser.extract(page, None)
        elif not isinstance(x, (str, bytes)):
            raise TypeError(f'Unexpected type {x.__class__.__name__} for a XPath attribute.')

        cache_name = f'{target}#ETree'

        if cache_name in cache:
            tree = cache[cache_name]
        else:
            tree = parse(x)
            cache[cache_name] = tree

        result = tree.xpath(self.xpath)
        if self.only_first:
            result = result[0]

        return result
