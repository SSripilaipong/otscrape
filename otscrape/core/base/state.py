import os
from collections.abc import Hashable
from threading import Lock
from typing import Dict, Set, Any, List, Tuple
import pickle

from .page.page import PageBase
from otscrape.core.base.exception import StateOnWaitingException


def ensure_key(key):
    if isinstance(key, PageBase):
        if not hasattr(key, 'key'):
            raise ValueError(f'Attribute named "key" is required in Page {key.__class__.__name__} to use State.')
        key = key['key']

    return key


def ensure_keys(keys):
    if isinstance(keys, (list, tuple)) or (not isinstance(keys, str) and hasattr(keys, '__iter__')):
        return [ensure_key(key) for key in keys]

    return [ensure_key(keys)]


class MemoryState:
    def __init__(self, name=None, parent=None):
        assert isinstance(name, Hashable)
        self.name = name or None  # type: Hashable
        self.path = parent.get_subpath(name) if parent else ()  # type: Tuple[Hashable]

        if parent:
            self.save = parent.save

        self.wait_list = {}  # type: Dict[Tuple[Hashable], MemoryState]
        self.notify_list = {}  # type: Dict[Tuple[Hashable], MemoryState]
        self.complete_list = {}  # type: Dict[Tuple[Hashable], MemoryState]

        self._running_number = 0
        self._complete = False
        self._holding = False

        self._lock = Lock()

    def get_subpath(self, name):
        path = (*self.path, name)
        return path

    def reset(self):
        self._running_number = 0

    def __setstate__(self, state):
        self.__dict__ = state
        self._lock = Lock()
        self.reset()

    def __getstate__(self):
        with self._lock:
            state = self.__dict__.copy()
        del state['_lock']
        return state

    def wait_for(self, other, notify=True):
        assert isinstance(other, MemoryState)

        with self._lock:
            self.wait_list[other.path] = other

        if notify:
            with other._lock:
                other.notify_list[self.path] = self

    def hold(self):
        with self._lock:
            self._holding = True

    def release(self):
        with self._lock:
            self._holding = False

    def notify(self, other):
        with self._lock:
            assert other.path in self.wait_list
            self.wait_list.pop(other.path)
            self.complete_list[other.path] = other

        self.try_complete()

    def try_complete(self):
        try:
            self.complete()
        except StateOnWaitingException:
            pass

    def complete(self):
        with self._lock:
            if self.wait_list:
                raise StateOnWaitingException()

            assert not self._complete and not self.wait_list

            holding = self._holding

        if not holding:
            with self._lock:
                self._complete = True

            for p in list(self.notify_list.keys()):
                with self._lock:
                    state = self.notify_list.pop(p)
                state.notify(self)

        self.save()

    def is_complete(self, state=None, name=None):
        if state or name:
            if state:
                path = state.path
            else:
                name = ensure_key(name)
                path = self.get_subpath(name)

            with self._lock:
                return path in self.complete_list
        else:
            with self._lock:
                return self._complete

    def is_waiting(self, state):
        with self._lock:
            return state.path in self.wait_list

    def _create_memory_instance(self, name):
        return MemoryState(name=name, parent=self)

    def _create_substate(self, path, wait=True, notify=True):
        with self._lock:
            state = self.wait_list.get(path, None)

        if state is None:
            state = self._create_memory_instance(path[-1])

        assert not self.is_complete(state)

        if wait:
            self.wait_for(state, notify=notify)

        return state

    def substate(self, name=None, suffix=None):
        assert name or suffix

        if name is None:
            with self._lock:
                key = 'step{i}:{suffix}'.format(suffix=suffix, i=self._running_number)
                self._running_number += 1
        else:
            key = ensure_key(name)

        path = self.get_subpath(key)

        self._lock.acquire()
        assert path not in self.notify_list

        if path in self.complete_list:
            ss = self.complete_list[path]
            self._lock.release()
        elif path in self.wait_list:
            ss = self.wait_list[path]
            self._lock.release()
        else:
            self._lock.release()
            ss = self._create_substate(path)

        return ss

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if not exc_type and not self.is_complete():
            self.complete()

    def iter(self, it, if_exists='skip', key=None):
        if self.is_complete():
            return

        if_exists = if_exists.lower().strip()
        assert if_exists in ('skip', 'skipall', 'stop')

        skipall = False
        state = self.substate(suffix='iter')
        state.hold()

        for x in it:
            if key:
                k = key(x)
            else:
                k = x

            if state.is_complete(name=k):
                if skipall:
                    continue

                if if_exists == 'skip':
                    continue
                elif if_exists == 'skipall':
                    skipall = True
                    continue
                elif if_exists == 'stop':
                    break

            ss = state.substate(k)
            ss.hold()

            yield ss, x

            ss.release()
            ss.try_complete()

        state.release()
        state.try_complete()


class PickleStateBase(MemoryState):
    def __init__(self, filename=None):
        self.filename = filename or 'state.pickle'

        super().__init__()

    @staticmethod
    def exists(filename):
        return os.path.exists(filename)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)

    @staticmethod
    def clean(filename):
        if os.path.exists(filename):
            os.remove(filename)

    def save(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self, file)


def PickleState(filename, replace=False):
    exists = PickleStateBase.exists(filename)

    if replace:
        if exists:
            PickleStateBase.clean(filename)
    elif exists:
        return PickleStateBase.load(filename)

    return PickleStateBase(filename)
