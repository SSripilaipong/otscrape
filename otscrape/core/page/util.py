from otscrape.core.base.data_model import DataModelMeta


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
