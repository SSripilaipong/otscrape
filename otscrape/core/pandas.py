from typing import Union, Iterable

import pandas as pd
from pandas import DataFrame, Series

from otscrape.core.base.page import Page
from otscrape.core.worker import Workers


def scrape_series(ss):
    if not ss.apply(lambda t: isinstance(t, Page) or pd.isnull(t)).all():
        raise ValueError('Values must be of type Page.')

    nonull = ss.dropna()

    with Workers() as w:
        buffer = w.scrape(nonull)
        data = [d.get_data() for d in buffer]

    df = DataFrame(data)
    df.index = nonull.index
    df = df.reindex(ss.index)

    return df


def scrape_pandas(data: Union[Series, DataFrame], column=None, full=False, drop=False, prefix=None, suffix=None):
    if isinstance(data, Series):
        return scrape_series(data)

    elif isinstance(data, DataFrame):
        assert column is not None

        ss = data[column]
        if len(ss.shape) > 1:
            raise ValueError(f'Columns named "{column}" is duplicated.')

        ext = scrape_series(ss)

        if full:
            prefix = prefix or column + '.'
            suffix = suffix or ''
            ext.columns = prefix + ext.columns + suffix

            if drop:
                data = data.drop(columns=[column])
            return pd.concat([data, ext], axis=1)

        prefix = prefix or ''
        suffix = suffix or ''
        ext.columns = prefix + ext.columns + suffix
        return ext

    elif isinstance(data, Iterable):
        return scrape_series(pd.Series([x for x in data]))

    raise TypeError(f'Type of data must be one of Pandas\'s data structures or Iterable')
