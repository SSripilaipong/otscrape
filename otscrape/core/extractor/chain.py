from typing import List, Callable, Union

from otscrape.core.base.extractor import Extractor
from .lambda_ import Lambda


class Chain(Extractor):
    def __init__(self, extractors: List[Union[Extractor, Callable]], *, target=None, project=True):
        super().__init__(target=target, project=project)

        self.extractors = [e if isinstance(e, Extractor) else Lambda(e) for e in extractors]

    def extract(self, page, cache):
        result = page[self.target]
        for e in self.extractors:
            result = {e.target: result}
            result = e(result)
        return result

    def __str__(self):
        return f'Chain({self.extractors})'
