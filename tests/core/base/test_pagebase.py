from otscrape import Page, Attribute, DummyLoader, Extractor


def test_attribute():
    class TestPage(Page):
        loader = ...
        a = Attribute()

        def __init__(self):
            super().__init__()

            self['a'] = 1234

    page = TestPage()
    assert page['a'] == 1234


def test_loader():
    class TestPage(Page):
        loader = DummyLoader('abcd')

    page = TestPage()
    assert page['raw'] == 'abcd'


def test_extractor_class():
    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPage(Page):
        loader = DummyLoader('abcd')

        first = FirstChar()

    p = TestPage()

    assert p['first'] == 'a'


def test_get_data():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPage(Page):
        loader = DummyLoader('    abcd')

        strip = Strip()
        first = FirstChar(strip)

    p = TestPage()

    assert p.get_data() == {'strip': 'abcd', 'first': 'a'}


def test_get_data_no_project():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPage(Page):
        loader = DummyLoader('    abcd')

        strip = Strip(project=False)
        first = FirstChar(strip)

    p = TestPage()

    assert p.get_data() == {'first': 'a'}


def test_extractor_error():
    class FirstChar(Extractor):
        def extract(self, page):
            raise Exception()

    class TestPage(Page):
        loader = DummyLoader('abcd')

        first = FirstChar()

    p = TestPage()

    assert p['first'] is None


def test_extractor_error_default_value():
    class FirstChar(Extractor):
        def extract(self, page):
            raise Exception()

    class TestPage(Page):
        loader = DummyLoader('abcd')

        first = FirstChar(replace_error='999')

    p = TestPage()

    assert p['first'] == '999'


def test_serial_extractor():
    class Strip(Extractor):
        def extract(self, page):
            return page[self.target].strip()

    class FirstChar(Extractor):
        def extract(self, page):
            return page[self.target][0]

    class TestPage(Page):
        loader = DummyLoader('    abcd')

        strip = Strip()
        first = FirstChar(strip)

    p = TestPage()

    assert p['first'] == 'a'
