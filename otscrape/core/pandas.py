import inspect

import pandas as pd
from pandas import DataFrame, Series

from otscrape.core.base.page import Page
from otscrape.core.worker import Workers


def pd_override(parent):
    def dec(cls):
        def wrap(m):
            def f(*args, **kwargs):
                r = m(*args, **kwargs)
                if isinstance(r, DataFrame):
                    r = PageDataFrame(r)
                elif isinstance(r, Series):
                    r = PageSeries(r)
                return r
            return f

        for name, method in inspect.getmembers(parent, predicate=inspect.isfunction):
            setattr(cls, name, wrap(method))

        return cls
    return dec


@pd_override(DataFrame)
class PageDataFrame(DataFrame):
    def expand(self, column, prefix=None, inplace=False):
        if not isinstance(self[column], PageSeries):
            raise TypeError(f'Column {column} needs to be of type PageSeries.')

        d = self[column].expand()

        if not prefix:
            prefix = column + '.'

        r = self._concat_or_return(d, prefix, inplace)
        if inplace:
            self.drop(columns=[column], inplace=True)
        else:
            return r.drop(columns=[column])

    def explode_json(self, column, prefix=None, inplace=False):
        d = pd.json_normalize(self[column])

        if not prefix:
            prefix = column + '.'

        r = self._concat_or_return(d, prefix, inplace)
        if inplace:
            self.drop(columns=[column], inplace=True)
        else:
            return r.drop(columns=[column])

    def _concat_or_return(self, d, prefix, inplace):
        t = self if inplace else self.copy()

        for c in d.columns:
            t[prefix + c] = d[c]

        if not inplace:
            return t


@pd_override(Series)
class PageSeries(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _check_datatypes(self):
        if not self.apply(lambda t: isinstance(t, Page) or pd.isnull(t)).all():
            raise ValueError('Values must be of type Page.')

    def expand(self):
        self._check_datatypes()

        nonull = self.dropna()

        with Workers() as w:
            buffer = w.scrape(nonull)
            data = [d.get_data() for d in buffer]

        df = PageDataFrame(data)
        df.index = nonull.index
        df = df.reindex(self.index)

        return df


def to_dataframe(pages):
    return PageSeries(pages).expand()
