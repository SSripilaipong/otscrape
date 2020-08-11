from requests import Response
from otscrape.base.attribute import Attribute


class RequestText(Attribute):
    def __init__(self, target=None, *, bytes_result=False, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.bytes_result = bytes_result

    def extract(self, page):
        target = self.target
        assert isinstance(page[target], Response)

        if self.bytes_result:
            return page[target].content

        return page[target].text


class RequestStatusCode(Attribute):

    def extract(self, page):
        target = self.target
        assert isinstance(page[target], Response)

        return page[target].status_code


class RequestJSON(Attribute):

    def extract(self, page):
        target = self.target
        assert isinstance(page[target], Response)

        return page[target].json()
