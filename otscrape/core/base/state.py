import os
from threading import Lock
import pickle

from .page import Page


def ensure_key(key):
    if isinstance(key, Page):
        assert hasattr(key, 'key')
        key = key['key']

    return key


class MemoryState:
    def __init__(self, replace=False, parent=None, do_load=True):
        self.parent = parent
        self.state_lock = Lock()

        self.visited = set()
        self.visiting = {}

        self._complete_lock = Lock()
        self._complete = False

        if not self.parent:
            if do_load:
                if replace:
                    self.clean()
                elif self.exists():
                    self.load()
        else:
            self.state_lock = self.parent.state_lock

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.complete()

    def get_data(self):
        data = {
            'visited': self.visited,
            'visiting': {k: v.get_data() if v else v for k, v in self.visiting.items()},
            '_complete': self._complete,
        }
        return data

    def iter(self, it, if_exists='skip'):
        if_exists = if_exists.lower().strip()
        assert if_exists in ('skip', 'skipall', 'stop')

        skipall = False
        for x in it:
            if self.is_visited(x):
                if skipall:
                    continue

                if if_exists == 'skip':
                    continue
                elif if_exists == 'skipall':
                    skipall = True
                    continue
                elif if_exists == 'stop':
                    return

            ss = self.visit(x)
            yield ss, x

            ss.complete()
            self.done(x)

    def break_loop(self, key):
        key = ensure_key(key)
        ss = self.visiting[key]

        ss.complete()
        self.done(key)

    def complete(self):
        with self._complete_lock:
            assert not self._complete and len(self.visiting) == 0

            self._complete = True

    def is_complete(self):
        with self._complete_lock:
            return self._complete

    def is_visited(self, key):
        key = ensure_key(key)
        return key in self.visited

    def visit(self, key):
        key = ensure_key(key)
        assert not self.is_visited(key)

        sub = self.visiting.get(key, MemoryState(parent=self))
        with self.state_lock:  # lock then writing
            self.visiting[key] = sub
        return sub

    def done(self, key):
        key = ensure_key(key)
        assert key in self.visiting

        sub = self.visiting[key]
        assert sub is None or (isinstance(sub, MemoryState) and sub.is_complete())

        self.visiting.pop(key)
        self.visited.add(key)

        with self.state_lock:
            self._save()

    def exists(self):
        return False

    def load(self):
        pass

    def _save(self):
        if self.parent:
            self.parent.save()
        else:
            self.save()

    def save(self):
        pass

    def clean(self):
        pass

    @classmethod
    def build_from_dict(cls, data, parent=None):
        if data is None:
            return data

        s = MemoryState(do_load=False, parent=parent)

        s.visited = data['visited']
        s._complete = data['_complete']
        s.visiting = {k: cls.build_from_dict(v, parent=s) for k, v in data['visiting'].items()}

        return s


class FileState(MemoryState):
    def __init__(self, filename=None, replace=False):
        self.filename = filename or 'state.pickle'

        super().__init__(replace=replace)

    def exists(self):
        return os.path.exists(self.filename)

    def load(self):
        with open(self.filename, 'rb') as file:
            data = pickle.load(file)

            s = MemoryState.build_from_dict(data, parent=self)

            self.visiting = s.visiting
            self.visited = s.visited
            self._complete = s._complete

    def save(self):
        with open(self.filename, 'wb') as file:
            data = self.get_data()
            pickle.dump(data, file)

    def clean(self):
        os.remove(self.filename)
