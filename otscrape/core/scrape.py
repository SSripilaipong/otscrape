from typing import Union, List, Dict
from collections.abc import Iterable

from otscrape.base import Page

PagesType = Union[List[Page], Page]
ProjectionType = Union[None, Dict[str, Union[str, 'ProjectionType']]]


def _set_chain_key_value(data, keys, value):
    *keys_prev, key = keys
    if keys_prev:
        for k in keys_prev:
            data = data[k]
    data[key] = value


def iter_attributes(page):
    result = {}
    queue = [((k,), v) for k, v in page.get_data().items()]

    while queue:
        (keys, value), *queue = queue

        if isinstance(value, Page):
            _set_chain_key_value(result, keys, {})
            queue += [((*keys, k), v) for k, v in value.get_data().items()]
        elif isinstance(value, dict):
            _set_chain_key_value(result, keys, {})
            queue += [((*keys, k), v) for k, v in value.items()]
        elif isinstance(value, str) or isinstance(value, bytes):
            _set_chain_key_value(result, keys, value)
        elif isinstance(value, Iterable):
            value = list(value)
            _set_chain_key_value(result, keys, [None] * len(value))
            queue += [((*keys, k), v) for k, v in enumerate(value)]
        else:
            _set_chain_key_value(result, keys, value)
    return result


def scrape(pages: PagesType, projection: ProjectionType = None):
    if projection is None:
        return iter_attributes(pages)

    pass
