from requests import Response

from otscrape.core.base.attribute import Attribute
from .text.etree import parse
from .request import RequestText


class XPath(Attribute):
    def __init__(self, target=None, xpath='.', *, only_first=False, encoding=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.xpath = xpath
        self.only_first = only_first
        self._req_parser = RequestText(target, encoding=encoding)

    def extract(self, page):
        target = self.target
        x = page[target]

        if isinstance(x, Response):
            x = self._req_parser.extract(page)
        elif not isinstance(x, (str, bytes)):
            raise TypeError(f'Unexpected type {x.__class__.__name__} for a XPath attribute.')

        cache_name = f'{target}#ETree'

        if cache_name in page.cached:
            tree = page.cached[cache_name]
        else:
            tree = parse(x)
            page.cached[cache_name] = tree

        result = tree.xpath(self.xpath)
        if self.only_first:
            result = result[0]

        return result
