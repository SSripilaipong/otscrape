from tempfile import NamedTemporaryFile
from requests import Response
from otscrape import Page, RequestText, DataPage, JSONLinePage, DictPath, CSVLinePage


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


def test_data_page():
    class TestPage(DataPage):
        pass

    p = TestPage('Hello')
    assert p['raw'] == 'Hello'


def test_JSONLinePage():
    with NamedTemporaryFile('w') as f:
        f.file.writelines(['{"a":1, "b":"Hello"}\n',
                           '{"a":2, "b":"World"}\n',
                           '{"a":3, "c":"Hello"}\n'])
        f.file.flush()

        class TestLinePage(JSONLinePage):
            _loader__filenames = f.name

            a = DictPath('/a')
            b = DictPath('/b')
            c = DictPath('/c')

        ls = list(TestLinePage.iter_lines())
        result = [{'a': 1, 'b': 'Hello', 'c': None},
                  {'a': 2, 'b': 'World', 'c': None},
                  {'a': 3, 'b': None,    'c': 'Hello'}]
        assert [x.get_data() for x in ls] == result


def test_CSVLinePage():
    with NamedTemporaryFile('w') as f:
        f.file.writelines(['a,b,c\n',
                           '1,Hello,123\n',
                           '2,World,456\n',
                           '3,"Hello, World",\n',
                           '4,"Hello, \n',
                           ' World",789\n'])
        f.file.flush()

        class TestLinePage(CSVLinePage):
            _loader__filenames = f.name

        ls = list(TestLinePage.iter_lines())
        result = [{'a': '1', 'b': 'Hello',           'c': '123'},
                  {'a': '2', 'b': 'World',           'c': '456'},
                  {'a': '3', 'b': 'Hello, World',    'c': ''},
                  {'a': '4', 'b': 'Hello, \n World', 'c': '789'}]

        assert [x['raw'] for x in ls] == result
