from otscrape.core.base.extractor import Extractor


class Raw(Extractor):
    def __init__(self, *, project=True, replace_error=None):
        super().__init__(target='raw', project=project, replace_error=replace_error)

    def extract(self, page, cache):
        return page[self.target]
