from typing import Iterator, Iterable

from otscrape.core.base.extractor import ExtractorBase, Extractor


class ZipDict(Extractor):
    def __init__(self, structure=None, *, project=True, replace_error=None):
        super().__init__(target=None, project=project, replace_error=replace_error)

        assert structure and all(isinstance(x, (str, ExtractorBase)) for x in structure.values())
        self.structure = structure

    def extract(self, page, cache):
        iter_dict = {}
        for key, value in self.structure.items():
            if isinstance(page[value], Iterable):
                v = iter(page[value])
            else:
                v = page[value]

            iter_dict[key] = v

        result = []
        try:
            while True:
                row = {}

                for key, it in iter_dict.items():
                    if isinstance(it, Iterator):
                        v = next(it)
                    else:
                        v = it

                    row[key] = v
                result.append(row)
        except StopIteration:
            pass

        return result
