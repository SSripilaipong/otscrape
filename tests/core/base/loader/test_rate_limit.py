import pytest

import time
import math

import otscrape as ot


class MyPage(ot.DataPage):
    _loader__rate_limit = '2/2'

    my_number = ot.Raw()


n_tasks = 10

n, s = map(float, MyPage.loader.rate_limit.split('/'))
min_complete_time = (math.ceil(n_tasks/n)-1)*s


@pytest.mark.slow
def test_sequential():
    start_ts = time.time()

    for i, x in enumerate(MyPage(i).get_data() for i in range(n_tasks)):
        assert x['my_number'] == i

    end_ts = time.time()
    dt = end_ts - start_ts

    assert dt > min_complete_time


@pytest.mark.slow
def test_workers():
    numbers = set()

    start_ts = time.time()

    with ot.Workers() as w:
        buffer = w.scrape((MyPage(i) for i in range(10)))
        for x in buffer:
            numbers.add(x['my_number'])

    end_ts = time.time()
    dt = end_ts - start_ts

    assert numbers == set(range(10))
    assert dt > min_complete_time
