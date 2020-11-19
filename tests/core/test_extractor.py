from requests import Response
from otscrape import PageBase, Raw, DummyLoader, chain, Extractor, JSON, SoupFindAll, SoupSelect, extractor


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
