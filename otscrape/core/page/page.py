from otscrape.core.base.page import PageBase
from otscrape.core.loader.request import SimpleRequestLoader

from .util import get_page_meta


class Page(PageBase, metaclass=get_page_meta(SimpleRequestLoader)):
    loader = None
