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
