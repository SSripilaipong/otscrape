from otscrape.core.base.page import PageBase
from otscrape.core.loader import LineLoader

from .util import get_page_meta


class FileLinePage(PageBase, metaclass=get_page_meta(LineLoader, parallel=True)):
    loader = None

    @classmethod
    def iter_lines(cls):
        return (cls() for _ in range(cls.loader.tot_line))

    @classmethod
    def reset(cls):
        cls.loader.reset()
