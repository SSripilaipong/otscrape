from lxml import etree
from otscrape.core.base.attribute import Attribute


def parse(text):
    tree = etree.fromstring(text, etree.HTMLParser())
    return tree


class ETree(Attribute):
    def extract(self, page):
        x = page[self.target]
        assert isinstance(x, (str, bytes))

        return parse(x)

