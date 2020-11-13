from lxml import etree
from otscrape.core.base.extractor import Extractor


def parse(text):
    tree = etree.fromstring(text, etree.HTMLParser())
    return tree


class ETree(Extractor):
    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, (str, bytes))

        return parse(x)

