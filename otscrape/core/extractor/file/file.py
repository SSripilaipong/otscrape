from otscrape.core.base.extractor import Extractor
from otscrape.core.loader.file import LineObject


class FileContent(Extractor):
    def __init__(self, target=None, *, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.kwargs = kwargs

    def extract(self, page, cache):
        target = self.target
        x = page[target]
        assert isinstance(x, (LineObject,))

        return x.content


class FileName(Extractor):
    def __init__(self, target=None, *, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.kwargs = kwargs

    def extract(self, page, cache):
        target = self.target
        x = page[target]
        assert isinstance(x, (LineObject,))

        return x.filename
