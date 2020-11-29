from typing import List
from otscrape import Extractor


class ChainedExtractor(Extractor):
    def __init__(self, extractors, target=None, project=False):
        super().__init__(target=target, project=project)

        self.extractors = extractors

    def extract(self, page, cache):
        result = page[self.target]
        for e in self.extractors:
            result = {e.target: result}
            result = e.extract(result, cache)
        return result

    def __str__(self):
        return f'ChainedExtractor({self.extractors})'


def chain(extractors: List[Extractor], target=None, project=True):

    return ChainedExtractor(extractors, target=target, project=project)
