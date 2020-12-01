from otscrape.core.base.page import PageBase
from otscrape.core.loader.request import SimpleRequestLoader

from .util import get_page_meta


class Page(PageBase, metaclass=get_page_meta(SimpleRequestLoader)):
    loader = None

    def __init__(self, url=None, **kwargs):
        kwargs = dict(kwargs)
        kwargs['url'] = url

        super().__init__(**kwargs)
