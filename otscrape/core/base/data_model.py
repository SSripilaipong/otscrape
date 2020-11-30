from .extractor import ExtractorBase, Attribute


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        attr_ids = {}
        attrs = {}
        proj = set()

        # add attributes
        for obj_name, obj in dct.items():
            if isinstance(obj, ExtractorBase):
                attr_ids[id(obj)] = obj_name
                attrs[obj_name] = obj
                if getattr(obj, 'do_project', False):
                    proj.add(obj_name)

        # add attributes from parents
        for base in bases:
            for obj_name in getattr(base, '_project_attrs', set()):
                if obj_name not in attrs:
                    proj.add(obj_name)
            for obj_name in getattr(base, '_attrs', set()):
                if obj_name not in attrs:
                    attrs[obj_name] = getattr(base, obj_name)
        # dct_new = {**attrs, **dct}
        dct_new = dct.copy()

        dct_new['_attrs'] = attrs
        dct_new['_attribute_ids'] = attr_ids
        dct_new['_project_attrs'] = proj

        instance = super().__new__(mcs, name, bases, dct_new)
        return instance


class DataModel(metaclass=DataModelMeta):
    _attrs = {}  # name -> obj
    _project_attrs = set()  # names
    _attribute_ids = {}  # id -> name

    def __init__(self):
        self._attr_cached = {}  # name -> value

    def get_data(self):
        result = {}
        for key in self._attrs:
            if key in self._project_attrs:
                result[key] = self[key]
        return result

    def _get_or_compute_attr(self, name):
        if name not in self._attr_cached:
            self._attr_cached[name] = self._attrs[name](self)

        return self._attr_cached[name]

    def __setitem__(self, key, value):
        if key not in self._attrs:
            raise ValueError(f'Expected an existing attribute name. Got "{key}".')

        obj = self._attrs[key]
        if type(obj) is not Attribute:
            raise TypeError(f'Type of attribute "{key}" must be Attribute.')

        if key not in self._attr_cached:
            self._attr_cached[key] = value

    def __getitem__(self, key):
        if isinstance(key, ExtractorBase):
            id_ = id(key)
            if id_ not in self._attribute_ids:
                return key(self)
            else:
                name = self._attribute_ids[id_]

        elif isinstance(key, str):
            name = key
        else:
            raise TypeError(f'Attribute {key} should be of type str or ExtractorBase')

        return self._get_or_compute_attr(name)
