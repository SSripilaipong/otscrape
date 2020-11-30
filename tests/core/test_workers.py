import pytest

import otscrape as ot
import time


class ContentPage(ot.DataPage):
    data = ot.Raw()
    add_one = ot.Lambda(lambda t: t + 1)


class ListingPage(ot.DataPage):
    page = ot.DictPath('/page')
    children = ot.Chain([ot.DictPath('/children'), ot.Map(ContentPage)])


@pytest.mark.slow
@pytest.mark.integration
def test_scrape_iter_buffer():
    with ot.Workers(3) as w:
        buffer = w.scrape(ListingPage({'page': i, 'children': list(range(i, i+5))}) for i in range(5))

        children = []
        for x in buffer:
            children += x['children']

        result = [x['add_one'] for x in w.scrape(children)]

    assert len(result) == 5*5

    for i in range(1, 10):
        assert sum(1 for x in result if x == i) == -abs(5-i) + 5


@pytest.mark.slow
@pytest.mark.integration
def test_scrape_faster1():
    def delay_load(data):
        time.sleep(0.1)
        return 999

    do_load_ori = ContentPage.loader.do_load
    ContentPage.loader.do_load = delay_load

    try:
        start_ts = time.time()

        result = [ContentPage(999).get_data() for _ in range(20)]
        assert result == [{'data': 999, 'add_one': 1000}] * 20

        end_ts = time.time()
        time0 = end_ts - start_ts

        start_ts = time.time()
        with ot.Workers(3) as w:
            result = list(w.scrape(ContentPage(999) for _ in range(20)))
        assert [x.get_data() for x in result] == [{'data': 999, 'add_one': 1000}] * 20
        end_ts = time.time()
        time1 = end_ts - start_ts

        assert time1 < time0
    finally:
        ContentPage.loader.do_load = do_load_ori
