from requests import Response
from otscrape import Page, RequestText


def test_request_call_once(mocker):
    class TestPage(Page):
        text = RequestText()

    url = 'https://example.com/'
    p = TestPage(url=url)

    my_text = 'Hello World'

    class MyResponse(Response):
        def __init__(self):
            super().__init__()
            self.status_code = 200

        @property
        def text(self):
            return my_text

    req_mock = mocker.patch('requests.request', return_value=MyResponse())
    assert p['text'] == my_text
    req_mock.assert_called_once_with('GET', url=url)


def test_request_call_once_with_post(mocker):
    class TestPage(Page):
        _loader__method = 'POST'

    url = 'https://example.com/'
    p = TestPage(url=url)

    class MyResponse(Response):
        def __init__(self):
            super().__init__()
            self.status_code = 200

    req_mock = mocker.patch('requests.request', return_value=MyResponse())
    _ = p['raw']
    req_mock.assert_called_once_with('POST', url=url)
