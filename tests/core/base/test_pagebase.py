from otscrape import PageBase, Attribute, DummyLoader, Extractor


def test_attribute():
    class TestPageBase(PageBase):
        loader = ...
        a = Attribute()

        def __init__(self):
            super().__init__()

            self['a'] = 1234

    page = TestPageBase()
    assert page['a'] == 1234


def test_loader():
    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')

    page = TestPageBase()
    assert page['raw'] == 'abcd'


def test_extractor_class():
    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')

        first = FirstChar()

    p = TestPageBase()

    assert p['first'] == 'a'


def test_get_data():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPageBase(PageBase):
        loader = DummyLoader('    abcd')

        strip = Strip()
        first = FirstChar(strip)

    p = TestPageBase()

    assert p.get_data() == {'strip': 'abcd', 'first': 'a'}


def test_get_data_no_project():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPageBase(PageBase):
        loader = DummyLoader('    abcd')

        strip = Strip(project=False)
        first = FirstChar(strip)

    p = TestPageBase()

    assert p.get_data() == {'first': 'a'}


def test_extractor_error():
    class FirstChar(Extractor):
        def extract(self, page):
            raise Exception()

    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')

        first = FirstChar()

    p = TestPageBase()

    assert p['first'] is None


def test_extractor_error_default_value():
    class FirstChar(Extractor):
        def extract(self, page):
            raise Exception()

    class TestPageBase(PageBase):
        loader = DummyLoader('abcd')

        first = FirstChar(replace_error='999')

    p = TestPageBase()

    assert p['first'] == '999'


def test_serial_extractor():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPageBase(PageBase):
        loader = DummyLoader('    abcd')

        strip = Strip()
        first = FirstChar(strip)

    p = TestPageBase()

    assert p['first'] == 'a'
