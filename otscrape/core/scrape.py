from typing import Union, List, Dict
from collections.abc import Iterable

from otscrape.base import Page, DataModel

PagesType = Union[List[Page], Page]
ProjectionType = Union[None, Dict[str, Union[str, 'ProjectionType']]]


def _iter_attributes(result):
    if isinstance(result, DataModel):
        result = result.get_data()
    elif isinstance(result, dict):
        tmp = {}
        for key, value in result.items():
            tmp[key] = _iter_attributes(value)
        result = tmp
    elif isinstance(result, str) or isinstance(result, bytes):
        return result
    elif isinstance(result, Iterable):
        result = [_iter_attributes(x) for x in result]

    return result


def scrape(pages: PagesType, projection: ProjectionType = None):
    if projection is None:
        return _iter_attributes(pages)

    pass
