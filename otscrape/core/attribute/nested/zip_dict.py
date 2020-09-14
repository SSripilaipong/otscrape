from typing import Iterator, Iterable

from otscrape.core.base.attribute import AttributeBase, Attribute


class ZipDict(Attribute):
    def __init__(self, structure=None, *, project=True, replace_error=None):
        super().__init__(target=None, project=project, replace_error=replace_error)

        assert structure and all(isinstance(x, (str, AttributeBase)) for x in structure.values())
        self.structure = structure

    def extract(self, page):
        iter_dict = {}
        for key, value in self.structure.items():
            if isinstance(page[value], Iterable):
                iter_dict[key] = iter(page[value])
            else:
                iter_dict[key] = page[value]

        result = []
        try:
            while True:
                row = {}
                for key, it in iter_dict.items():
                    if isinstance(it, Iterator):
                        row[key] = next(it)
                    else:
                        row[key] = it
                result.append(row)
        except StopIteration:
            pass

        return result
