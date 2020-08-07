try:
    from functools import cached_property
except ImportError:
    from .futures import cached_property


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        attrs = {}
        proj = set()

        # add attributes
        for name, obj in dct.items():
            if getattr(obj, 'is_attribute', None):
                attrs[name] = obj

            elif getattr(obj, 'is_extractor', None):
                def get_extract(extractor_object):
                    def extract(page):
                        return extractor_object._extract(page)
                    return extract
                attrs[name] = attribute(get_extract(obj), project=obj.do_project)

            else:
                continue

            if getattr(obj, 'do_project', False):
                proj.add(name)

        # add attributes from parents
        for base in bases:
            if not hasattr(base, '_attributes'):
                continue
            for name in getattr(base, '_attributes'):
                attrs[name] = getattr(base, name)
        dct_new = dict(dct)
        dct_new.update(attrs)

        dct_new['_attributes'] = set(attrs.keys())
        dct_new['_project_attrs'] = proj

        instance = super().__new__(mcs, name, bases, dct_new)
        return instance


class DataModel(metaclass=DataModelMeta):
    _attributes = []
    _project_attrs = set()

    def __init__(self):
        pass

    def get_data(self):
        result = {}
        for key in self._attributes:
            if key in self._project_attrs:
                result[key] = getattr(self, key)
        return result


def attribute(func=None, project=True):
    def _attribute(_func):
        wrapper = cached_property(_func)
        wrapper.is_attribute = True
        wrapper.do_project = project
        return wrapper

    if func is None:
        return _attribute

    return _attribute(func)
