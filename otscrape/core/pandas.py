from contextlib import contextmanager
from typing import Union, Iterable, Callable

import pandas as pd
from pandas import DataFrame, Series

from otscrape.core.base.page import PageBase
from otscrape.core.worker import Workers


def _scrape_chunk(chunk, workers=None):
    if workers:
        buffer = workers.scrape(chunk, buffer='order')
        data = [d.get_data() for d in buffer]
    else:
        data = [d.get_data() for d in chunk]

    return data


@contextmanager
def dummy_context():
    yield None


def _scrape_series(ss, chunk_size: Union[int, None] = None, stop_if: Union[Callable, None] = None,
                   n_workers: Union[int, None] = -1):
    if not ss.apply(lambda t: isinstance(t, PageBase) or pd.isnull(t)).all():
        raise ValueError('Values must be of type Page.')

    nonull = ss.dropna()

    if n_workers == 1 or n_workers is None:
        workers = dummy_context()
    else:
        workers = Workers(n_workers)

    data = []
    with workers as w:
        if chunk_size:
            for i in range(0, nonull.shape[0], chunk_size):
                chunk = _scrape_chunk(nonull.iloc[i: i+chunk_size], workers=w)

                if stop_if:
                    filtered = [x for x in chunk if not stop_if(x)]
                    data += filtered

                    if len(filtered) < len(chunk):
                        break
                else:
                    data += chunk
        else:
            data = _scrape_chunk(nonull, workers=w)

    df = DataFrame(data)
    df.index = nonull.index
    df = df.reindex(ss.index)

    return df


def scrape_pandas(data: Union[Series, DataFrame, Iterable], column=None, full=False, drop=False,
                  chunk_size: Union[int, None] = None, stop_if: Union[Callable, None] = None,
                  n_workers: Union[int, None] = -1,
                  prefix=None, suffix=None):
    if isinstance(data, Series):
        return _scrape_series(data, chunk_size=chunk_size, stop_if=stop_if, n_workers=n_workers)

    elif isinstance(data, DataFrame):
        assert column is not None

        ss = data[column]
        if len(ss.shape) > 1:
            raise ValueError(f'Columns named "{column}" is duplicated.')

        ext = _scrape_series(ss, chunk_size=chunk_size, stop_if=stop_if, n_workers=n_workers)

        if full:
            prefix = prefix if prefix is not None else column + '.'
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
        return _scrape_series(pd.Series([x for x in data]), chunk_size=chunk_size, stop_if=stop_if, n_workers=n_workers)

    raise TypeError(f'Type of data must be one of Pandas\'s data structures or Iterable')
