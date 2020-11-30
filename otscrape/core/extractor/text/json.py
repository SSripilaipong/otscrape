import json

from otscrape.core.base.extractor import Extractor


class JSONDict(Extractor):
    def __init__(self, target=None, *, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.kwargs = kwargs

    def extract(self, page, cache):
        target = self.target
        assert isinstance(page[target], (str, bytes))

        return json.loads(page[target], **self.kwargs)
