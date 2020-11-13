from typing import List
from otscrape import Extractor


def chain(extractors: List[Extractor], target=None, project=True):
    class ChainedExtractor(Extractor):
        def extract(self, page, cache):
            result = page[self.target]
            for e in extractors:
                result = {e.target: result}
                result = e.extract(result, cache)
            return result

        def __str__(self):
            return f'ChainedExtractor({extractors})'

    return ChainedExtractor(target=target, project=project)
