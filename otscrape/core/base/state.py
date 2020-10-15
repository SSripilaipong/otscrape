import os
from typing import Dict, Set, Any
import pickle

from .page import Page


def ensure_key(key):
    if isinstance(key, Page):
        if not hasattr(key, 'key'):
            raise ValueError(f'Attribute named "key" is required in Page {key.__class__.__name__} to use State.')
        key = key['key']

    return key


class MemoryState:
    def __init__(self, name=None, parent=None):
        self.name = name or 'root'
        self.parent = parent  # type: MemoryState

        self.visited = set()  # type: Set[Any]
        self.visiting = {}  # type: Dict[Any, MemoryState]

        self._running_number = 0
        self._complete = False

    def get_data(self, recursive=True):
        if recursive:
            visiting = {k: v.get_data() if v else v for k, v in self.visiting.items()}
        else:
            visiting = self.visiting

        data = {
            'name': self.name,
            'visited': self.visited,
            'visiting': visiting,
            '_complete': self._complete,
        }
        return data

    def set_data(self, data):
        self.name = data['name']
        self.visited = data['visited']
        self.visiting = data['visiting']
        self._complete = data['_complete']

    def complete(self):
        assert not self._complete and len(self.visiting) == 0

        self._complete = True

    def is_complete(self):
        return self._complete

    def is_visited(self, key):
        key = ensure_key(key)
        return key in self.visited

    def _create_memory_instance(self, name):
        return MemoryState(name=name, parent=self)

    def create_substate(self, name):
        assert not self.is_visited(name)

        sub = self.visiting.get(name, None)
        if sub is None:
            sub = self._create_memory_instance(name)

        self.visiting[name] = sub
        return sub

    def done(self, key):
        key = ensure_key(key)
        assert key in self.visiting

        sub = self.visiting[key]
        assert isinstance(sub, MemoryState) and sub.is_complete()

        self.visiting.pop(key)
        self.visited.add(key)

    @classmethod
    def build_from_dict(cls, data, parent):
        if data is None:
            return data

        s = cls(data['name'], parent)

        s.visited = data['visited']
        s._complete = data['_complete']
        s.visiting = {k: cls.build_from_dict(v, parent=s) for k, v in data['visiting'].items()}

        return s

    def get_fullname(self):
        s = self
        names = []
        while s.parent:
            names.append(s.name)
            s = s.parent

        return list(reversed(names))

    def get_substate(self, keys):
        ss = self

        for key in keys:
            ss = ss.visiting.get(key, None)
            if ss is None:
                raise ValueError(f'State of key {key} is not found.')

        return ss

    def visit(self, key=None, suffix=None):
        assert key or suffix
        key = ensure_key(key)

        if key is None:
            key = 'step{i}:{suffix}'.format(suffix=suffix, i=self._running_number)
            self._running_number += 1

        if key in self.visiting:
            ss = self.visiting[key]
        else:
            ss = self.create_substate(key)

        return ss

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if not exc_type and not self._complete:
            self.complete()

    def iter(self, it, if_exists='skip'):
        if self._complete:
            return

        if_exists = if_exists.lower().strip()
        assert if_exists in ('skip', 'skipall', 'stop')

        skipall = False
        state = self.visit(suffix='iter')
        for x in it:
            if state.is_visited(x):
                if skipall:
                    continue

                if if_exists == 'skip':
                    continue
                elif if_exists == 'skipall':
                    skipall = True
                    continue
                elif if_exists == 'stop':
                    return

            ss = state.visit(x)

            yield ss, x

            ss.complete()
            state.done(x)

        state.complete()
        self.done(state.name)

    def break_loop(self, key):
        key = ensure_key(key)
        ss = self.visiting[key]

        ss.complete()
        self.done(key)


class SavableMemoryState(MemoryState):
    def __init__(self, name=None, parent=None, replace=False):
        super().__init__(name, parent)

        if not parent:
            if replace:
                if self.exists():
                    self.clean()
            elif self.exists():
                self.load()

    def _create_memory_instance(self, name):
        return SavableMemoryState(name=name, parent=self, replace=False)

    def exists(self):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def clean(self):
        raise NotImplementedError()

    def _save(self):
        if self.parent:
            self.parent._save()
        else:
            self.save()

    def done(self, key):
        super().done(key)

        self._save()

    def complete(self):
        super().complete()

        self._save()


class PickleState(SavableMemoryState):
    def __init__(self, filename=None, replace=False):
        self.filename = filename or 'state.pickle'

        super().__init__(replace=replace)

    def exists(self):
        return os.path.exists(self.filename)

    def get_data(self, recursive=True):
        data = super().get_data(recursive=recursive)
        data['filename'] = self.filename
        return data

    def set_data(self, data):
        super().set_data(data)
        self.filename = data['filename']

    def load(self):
        with open(self.filename, 'rb') as file:
            p = pickle.load(file)

            s = SavableMemoryState.build_from_dict(p, parent=self)

            data = s.get_data(recursive=False)
            data['filename'] = self.filename
            self.set_data(data)

    def save(self):
        with open(self.filename, 'wb') as file:
            data = self.get_data()
            pickle.dump(data, file)

    def clean(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
