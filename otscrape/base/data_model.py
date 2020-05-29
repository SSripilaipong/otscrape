from functools import wraps, cached_property
from collections.abc import Iterable


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        attrs = {}

        for name, obj in dct.items():
            if getattr(obj, 'is_attribute', None):
                attrs[name] = obj
            elif getattr(obj, 'is_extractor', None):
                attrs[name] = attribute(obj.extract)

        dct.update(attrs)
        dct['_attributes'] = set(attrs.keys())

        instance = super().__new__(mcs, name, bases, dct)
        return instance


class DataModel(metaclass=DataModelMeta):
    _attributes = None

    def __init__(self):
        pass

    def get_data(self):
        result = {}
        for key in self._attributes:
            result[key] = getattr(self, key)
        return result


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


def attribute(func):
    @wraps(func)
    def wrapper(self):
        result = func(self)
        return _iter_attributes(result)

    wrapper = cached_property(wrapper)
    wrapper.is_attribute = True
    return wrapper

