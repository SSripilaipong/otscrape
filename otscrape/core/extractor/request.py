from requests import Response
from otscrape.core.base.extractor import Extractor


class RequestText(Extractor):
    def __init__(self, target=None, *, bytes_result=False, encoding=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.bytes_result = bytes_result
        self.encoding = encoding

    def extract(self, page, cache):
        x = page[self.target]
        assert isinstance(x, Response)

        if self.bytes_result:
            return x.content
        elif self.encoding:
            return x.content.decode(self.encoding)

        return x.text


class RequestStatusCode(Extractor):

    def extract(self, page, cache):
        target = self.target
        assert isinstance(page[target], Response)

        return page[target].status_code


class RequestJSON(Extractor):

    def extract(self, page, cache):
        target = self.target
        assert isinstance(page[target], Response)

        return page[target].json()
