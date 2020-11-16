from otscrape.core.base.data_model import DataModelMeta
from otscrape.core.base.page import PageBase
from otscrape.core.loader.request import SimpleRequestLoader
from otscrape.core.loader import DummyLoader


def get_page_meta(loader_cls):
    class PageMeta(DataModelMeta):
        def __new__(mcs, name, bases, dct):
            dct_new = {}
            loader_params = {}
            loader_prefix = '_loader__'
            for key, value in dct.items():
                assert key != 'loader'

                if key.startswith(loader_prefix):
                    name = key[len(loader_prefix):]
                    loader_params[name] = value
                else:
                    dct_new[key] = value

            dct_new['loader'] = loader_cls(**loader_params)

            x = super().__new__(mcs, name, bases, dct_new)
            return x

    return PageMeta


class Page(PageBase, metaclass=get_page_meta(SimpleRequestLoader)):
    pass


class DummyPage(PageBase):
    loader = DummyLoader()

    def __init__(self, data):
        super().__init__(data=data)
