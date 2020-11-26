from requests import Response
from tempfile import NamedTemporaryFile

from otscrape import (PageBase, Raw, DummyLoader, chain, Extractor, JSON, SoupFindAll, SoupSelect, extractor,
                      FileLinePage, FileContent, FileLineNumber, FileName)


def test_Raw():
    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')
        raw_project = Raw()

    p = TestPageBase()
    assert p.get_data() == {'raw_project': 'abcd'}


def test_chain():
    class Strip(Extractor):
        def extract(self, page, cache):
            return page[self.target].strip()

    class Pad0(Extractor):
        def __init__(self, target=None, n=1, *args, **kwargs):
            super().__init__(target=target, *args, **kwargs)
            self.n = n

        def extract(self, page, cache):
            return page[self.target] + ('0' * self.n)

    class Last(Extractor):
        def __init__(self, target=None, n=1, *args, **kwargs):
            super().__init__(target=target, *args, **kwargs)
            self.n = n

        def extract(self, page, cache):
            return page[self.target][-self.n:]

    class TestPageBase(PageBase):
        loader = DummyLoader('{"data":"   abcd   ","name":"Chain"}')

        result = chain([JSON(path='/data'), Strip(), Pad0(n=2), Last(n=4)])

    p = TestPageBase()
    assert p['result'] == 'cd00'


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
