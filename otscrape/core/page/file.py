from otscrape.core.base.page import PageBase
from otscrape.core.loader import LineLoader
from otscrape.core.base import share

from .util import get_page_meta


class FileLinePage(PageBase, metaclass=get_page_meta(LineLoader, parallel=True)):
    loader = None

    @classmethod
    def iter_lines(cls):
        return (cls() for _ in range(cls.loader.tot_line))

    @classmethod
    def apply(cls, filenames):
        if not share.is_worker:
            raise EnvironmentError('apply() only available when using in Workers.')

        loader_tmp = cls.loader
        loader = LineLoader(filenames, loader_tmp.rate_limit, loader_tmp.fetch_size,
                            parallel=False, **loader_tmp.kwargs)
        cls.loader = loader

        result = []
        for x in (cls() for _ in range(cls.loader.tot_line)):
            x.get_data()
            result.append(x)

        cls.loader = loader_tmp

        return result

    @classmethod
    def reset(cls):
        cls.loader.reset()
