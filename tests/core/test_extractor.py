from requests import Response
from tempfile import NamedTemporaryFile

from otscrape import (PageBase, Raw, DummyLoader, Chain, ChainMap, Map, StarMap, Lambda, StarLambda, Extractor, JSON,
                      SoupFindAll, SoupSelect, extractor,
                      FileLinePage, FileContent, FileLineNumber, FileName, DataPage, DictPath)


class Strip(Extractor):
    def extract(self, page, cache):
        return page[self.target].strip()


class Pad0(Extractor):
    def __init__(self, target=None, n=1, *args, **kwargs):
        super().__init__(target=target, *args, **kwargs)
        self.n = n

    def extract(self, page, cache):
        return page[self.target] + ('0' * self.n)


class First(Extractor):
    def extract(self, page, cache):
        return page[self.target][0]


class Last(Extractor):
    def __init__(self, target=None, n=1, *args, **kwargs):
        super().__init__(target=target, *args, **kwargs)
        self.n = n

    def extract(self, page, cache):
        return page[self.target][-self.n:]


def test_Raw():
    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')
        raw_project = Raw()

    p = TestPageBase()
    assert p.get_data() == {'raw_project': 'abcd'}


def test_Chain():
    class TestPage(DataPage):
        result = Chain([JSON(path='/data'), Strip(), Pad0(n=2), Last(n=4)])
        error = Chain([JSON(path='/data'), Strip(), Lambda(lambda t: t[20], replace_error='error'), Last(n=4)])
        upper = Chain([JSON(path='/name'), str.upper])

    p = TestPage('{"data":"   abcd   ","name":"Chain"}')

    assert p['result'] == 'cd00'
    assert p['error'] == 'rror'
    assert p['upper'] == 'CHAIN'


def test_ChainMap():
    class TestPage(DataPage):
        data = ChainMap([JSON(path='/data'), Strip(), Pad0(n=2), Last(n=4)])
        errors = ChainMap([JSON(path='/data'), Strip(),
                           Lambda(lambda t: str(int(t)), replace_error='error'), Last(n=4)])
        names = ChainMap([JSON(path='/name'), str.upper])

    p = TestPage([
        '{"data":"   abcd   ","name":"One"}',
        '{"data":"   efgh   ","name":"Two"}',
        '{"data":"   1234   ","name":"Scrape"}',
    ])

    assert p['data'] == ['cd00', 'gh00', '3400']
    assert p['errors'] == ['rror', 'rror', '1234']
    assert p['names'] == ['ONE', 'TWO', 'SCRAPE']


def test_Map():
    class TestPage(DataPage):
        to_int = Map(int, replace_error=0)
        to_float = Map(float)
        to_float_to_int = Map(int, to_float)

        to_float_to_str = Map(str, to_float)
        to_float_first_to_int = Map(First(), to_float_to_str)

    p = TestPage(['1.5', '2.4', '3'])

    assert p['to_int'] == [0, 0, 3]
    assert p['to_float'] == [1.5, 2.4, 3.0]
    assert p['to_float_to_int'] == [1, 2, 3]
    assert p['to_float_first_to_int'] == ['1', '2', '3']


def test_StarMap():
    class AddOne(Extractor):
        def extract(self, page, cache):
            return page[self.target] + 1

    class TestPage(DataPage):
        add = StarMap(lambda *, a, b: a+b, replace_error=0)
        add_one = StarMap(AddOne(), add)

    p = TestPage([{'a': 1, 'b': 2},
                  {'a': 2, 'b': 4},
                  {'a': 3, 'b': 9}])

    assert p['add'] == [3, 6, 12]
    assert p['add_one'] == [4, 7, 13]


def test_Lambda():
    class TestPage(DataPage):
        with_0 = Lambda(lambda x: x + ['0'])
        to_float = Lambda(lambda x: list(map(float, x)))

        error = Lambda(lambda x: x/0, replace_error=[])

    p = TestPage(['1.5', '2.4'])

    assert p.get_data() == {'with_0': ['1.5', '2.4', '0'], 'to_float': [1.5, 2.4], 'error': []}


def test_StarLambda():
    class TestPage(DataPage):
        array = DictPath('/array')
        data = DictPath('/dict')

        array_to_float = Map(float, array)

        sum_array = StarLambda(lambda a, b: a + b, array_to_float)
        sum_dict = StarLambda(lambda a, b: a + b, data)

    p = TestPage({'array': ['1.5', '2.4'], 'dict': {'a': 1.5, 'b': 2.4}})

    assert p['sum_array'] == p['sum_dict'] == 3.9


def test_SoupFindAll_with_text():
    class TestPageBase(PageBase):
        loader = DummyLoader('<html><body><h1 id="head1">Hello World</h1><h1 id="head2">otscrape!</h1></body></html>')

        elements = SoupFindAll('h1')

        @extractor
        def texts(self):
            return [e.get_text() for e in self['elements']]

    p = TestPageBase()

    assert p['texts'] == ['Hello World', 'otscrape!']


def test_SoupFindAll_with_Response():
    my_text = '<html><body><h1 id="head1">Hello World</h1><h1 id="head2">otscrape!</h1></body></html>'

    class MyResponse(Response):
        def __init__(self):
            super().__init__()
            self.status_code = 200

        @property
        def text(self):
            return my_text

    class TestPageBase(PageBase):
        loader = DummyLoader(MyResponse())

        elements = SoupFindAll('h1')

        @extractor
        def texts(self):
            return [e.get_text() for e in self['elements']]

    p = TestPageBase()

    assert p['texts'] == ['Hello World', 'otscrape!']
    assert p._cached['raw#Soup']


def test_SoupSelect():
    my_text = '<html><body><h1 id="head1">Hello World</h1><h1 id="head2"><b>otscrape!</b></h1></body></html>'

    class TestPageBase(PageBase):
        loader = DummyLoader(my_text)

        elements = SoupSelect('h1 > b')

        @extractor
        def texts(self):
            return [e.get_text() for e in self['elements']]

    p = TestPageBase()

    assert p['texts'] == ['otscrape!']


def test_SoupSelect_one():
    my_text = '<html><body><h1 id="head1">Hello World</h1><h1 id="head2"><b>otscrape!</b></h1></body></html>'

    class TestPageBase(PageBase):
        loader = DummyLoader(my_text)

        element = SoupSelect('h1 > b', multiple=False)

        @extractor
        def text(self):
            return self['element'].get_text()

    p = TestPageBase()

    assert p['text'] == 'otscrape!'


def test_file_extractor():
    with NamedTemporaryFile('w') as f:
        f.file.writelines(['Hello\n', 'World\n', '\n', 'One\n', 'Two\n', 'Scrape\n'])
        f.file.flush()

        class TestLinePage(FileLinePage):
            _loader__filenames = f.name

            line_content = FileContent()
            line_no = FileLineNumber()
            file_name = FileName()

        ls = list(TestLinePage.iter_lines())
        result = [{'line_content': 'Hello\n', 'line_no': 0, 'file_name': f.name},
                  {'line_content': 'World\n', 'line_no': 1, 'file_name': f.name},
                  {'line_content': '\n', 'line_no': 2, 'file_name': f.name},
                  {'line_content': 'One\n', 'line_no': 3, 'file_name': f.name},
                  {'line_content': 'Two\n', 'line_no': 4, 'file_name': f.name},
                  {'line_content': 'Scrape\n', 'line_no': 5, 'file_name': f.name}]
        assert [x.get_data() for x in ls] == result


def test_dict_extractor():
    class TestPage(DataPage):
        a = DictPath('/a')
        b = DictPath('/b[1]')
        c = DictPath('/c')
        d = DictPath('/d/y[-1]/p')

    p = TestPage({'a': 1, 'b': ['Hello', 'World'], 'd': {'x': 1, 'y': [7, 8, 9, {'p': 123}]}})

    assert p.get_data() == {'a': 1, 'b': 'World', 'c': None, 'd': 123}
