import json

from otscrape.core.base.attribute import Attribute


class JSONDict(Attribute):
    def __init__(self, target=None, *, encoding=None, project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.encoding = encoding
        self.kwargs = kwargs

    def extract(self, page):
        target = self.target
        assert isinstance(page[target], (str, bytes))

        return json.loads(page[target], encoding=self.encoding, **self.kwargs)
