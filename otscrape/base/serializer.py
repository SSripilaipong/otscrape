from functools import wraps, cached_property
from collections.abc import Iterable


class SerializerMeta(type):
    def __new__(mcs, name, bases, dct):
        attrs = {}

        for name, obj in dct.items():
            if not getattr(obj, 'is_attribute', None):
                continue

            attrs[name] = obj

        dct.update(attrs)
        dct['_attributes'] = set(attrs.keys())

        instance = super().__new__(mcs, name, bases, dct)
        return instance


class Serializer(metaclass=SerializerMeta):
    _attributes = None

    def __init__(self):
        pass

    def get_data(self):
        result = {}
        for key in self._attributes:
            result[key] = getattr(self, key)
        return result


def _iter_attributes(result):
    if isinstance(result, Serializer):
        result = result.get_data()
    elif isinstance(result, dict):
        tmp = {}
        for key, value in result.items():
            tmp[key] = _iter_attributes(value)
        result = tmp
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

