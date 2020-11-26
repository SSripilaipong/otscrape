from otscrape.core.base.page import PageBase
from otscrape.core.loader import DummyLoader
from .util import get_page_meta


class DataPage(PageBase, metaclass=get_page_meta(DummyLoader)):
    loader = None

    def __init__(self, data):
        super().__init__(data=data)
