import re

from otscrape.core.base.extractor import Extractor


key_pattern = re.compile(r'^[a-zA-Z_]+$')
key_index_pattern = re.compile(r'^[a-zA-Z_]+\[-?\d+\]$')


def get_item_from_path(d, path):
    assert path.startswith('/') and '//' not in path

    for key in (s for s in path.split('/') if s):
        if key_pattern.match(key):
            assert key in d
            d = d[key]
        elif key_index_pattern.match(key):
            name, index = key.split('[')
            index = int(index.strip(']'))

            assert name in d
            d = d[name]

            assert hasattr(d, '__getitem__')
            d = d[index]

    return d


class DictPath(Extractor):
    def __init__(self, path='/', target=None, *, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.path = path

    def extract(self, page, cache):
        target = self.target
        item = get_item_from_path(page[target], self.path)
        return item
