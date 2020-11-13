from otscrape import Page, Raw, DummyLoader


def test_Raw():
    class TestPage(Page):
        loader = DummyLoader('abcd')
        raw_project = Raw()

    p = TestPage()
    assert p.get_data() == {'raw_project': 'abcd'}
