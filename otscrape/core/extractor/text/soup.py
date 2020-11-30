from bs4 import BeautifulSoup

from otscrape.core.base.extractor import Extractor


class TextSoup(Extractor):
    def __init__(self, parser='html.parser', target=None, *, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.parser = parser
        self.kwargs = kwargs

    def extract(self, page, cache):
        target = self.target

        x = page[target]
        assert isinstance(x, (str, bytes))

        return BeautifulSoup(x, parser=self.parser, features='lxml', **self.kwargs)
