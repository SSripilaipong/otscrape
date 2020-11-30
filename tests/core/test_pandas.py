import pytest
import time
import pandas as pd

import otscrape as ot


class ContentPage(ot.DataPage):
    data = ot.Raw()
    add_one = ot.Lambda(lambda t: t + 1)

    @ot.extractor
    def slow(self):
        time.sleep(1)
        return 123


class ListingPage(ot.DataPage):
    page = ot.DictPath('/page')
    children = ot.Chain([ot.DictPath('/children'), ot.Map(ContentPage)])


@pytest.mark.slow
@pytest.mark.integration
def test_scrape():
    df = ot.scrape_pandas(ListingPage({'page': i, 'children': list(range(i, i+5))}) for i in range(5))
    assert df.shape == (5, 2)

    df = df.explode('children').reset_index(drop=True)

    a = ot.scrape_pandas(df, column='children', full=True)
    assert a.shape == (25, 5)

    b = ot.scrape_pandas(df, column='children', full=True, drop=True)
    assert b.shape == (25, 4)
