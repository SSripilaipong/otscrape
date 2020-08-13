try:
    from functools import cached_property
except ImportError:
    from .futures import cached_property

from .attribute import AttributeBase


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        attr_ids = {}
        attrs = {}
        proj = set()

        # add attributes
        for name, obj in dct.items():
            if isinstance(obj, AttributeBase):
                attr_ids[id(obj)] = name
                attrs[name] = cached_property(obj)
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
        dct_new['_attribute_ids'] = attr_ids
        dct_new['_project_attrs'] = proj

        instance = super().__new__(mcs, name, bases, dct_new)
        return instance


class DataModel(metaclass=DataModelMeta):
    _attributes = []
    _project_attrs = set()
    _attribute_ids = {}

    def __init__(self):
        pass

    def get_data(self):
        result = {}
        for key in self._attributes:
            if key in self._project_attrs:
                result[key] = getattr(self, key)
        return result

    def __getitem__(self, key):
        if isinstance(key, AttributeBase):
            id_ = id(key)
            if id_ in self._attribute_ids:
                key = self._attribute_ids[id_]
            else:
                raise ValueError(f'attribute {key} doesn\'t belong to this page')

        if isinstance(key, str):
            if key not in self._attributes:
                raise ValueError(f'attribute {key} not found')

            return getattr(self, key)
        else:
            raise TypeError(f'attribute {key} should be of type str or AttributeBase')
