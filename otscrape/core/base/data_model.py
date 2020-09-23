from .attribute import AttributeBase


class DataModelMeta(type):
    def __new__(mcs, name, bases, dct):
        attr_ids = {}
        attrs = {}
        proj = set()

        # add attributes
        for obj_name, obj in dct.items():
            if isinstance(obj, AttributeBase):
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
    _attrs = {}
    _project_attrs = set()
    _attribute_ids = {}

    def __init__(self):
        pass

    def get_data(self):
        result = {}
        for key in self._attrs:
            if key in self._project_attrs:
                result[key] = self[key]
        return result

    def __getitem__(self, key):
        if isinstance(key, AttributeBase):
            id_ = id(key)
            if id_ in self._attribute_ids:
                key = self._attribute_ids[id_]
                return self._attrs[key](self)
            else:
                return key(self, use_cache=False)

        elif isinstance(key, str):
            return self._attrs[key](self)
        else:
            raise TypeError(f'attribute {key} should be of type str or AttributeBase')
