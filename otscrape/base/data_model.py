from functools import cached_property


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        print(dct)
        attrs = {}

        for name, obj in dct.items():
            if getattr(obj, 'is_attribute', None):
                attrs[name] = obj
            elif getattr(obj, 'is_extractor', None):
                attrs[name] = attribute(obj.extract)

        for base in bases:
            if not hasattr(base, '_attributes'):
                continue
            for name in getattr(base, '_attributes'):
                attrs[name] = getattr(base, name)

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


def attribute(func):
    wrapper = cached_property(func)
    wrapper.is_attribute = True
    return wrapper

