from otscrape import PageBase, Raw, DummyLoader, chain, Extractor, JSON


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
