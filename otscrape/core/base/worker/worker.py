import os

from otscrape.core.base.state import MemoryState, PickleState
from otscrape.core.base.exception import FatalException
from otscrape.core.base.worker import CommandExecutor


def get_state(state, replace=False):
    if state is None:
        return None, False

    if isinstance(state, MemoryState):
        return state, False

    if isinstance(state, str):
        filename, ext = os.path.splitext(state)

        if ext.lower() == '.pickle':
            state = PickleState(state, replace=replace)
        else:
            raise NotImplementedError()

        state.__enter__()
        return state, True

    raise NotImplementedError()


class WorkersBase:
    def __init__(self, n_workers=None, state=None, restart=False):
        self._exporter_cache = {}
        self._executor = CommandExecutor(n_workers)

        self.state, self.__state_need_close = get_state(state, replace=restart)  # type: (MemoryState, bool)
        self.current_state = self.state  # type: MemoryState

    def iter(self, it, if_exists='skip', key=None):
        if not self.state:
            yield from it
            return

        current_state = self.current_state
        for ss, x in self.current_state.iter(it, if_exists=if_exists, key=key):
            self.current_state = ss

            try:
                yield x
            except GeneratorExit:
                break

        self.current_state = current_state

    def open(self):
        self._executor.open()
        self._exporter_cache = {}
        return self

    def close(self, force=False):
        self._executor.close(force=force)

        for exporter in self._exporter_cache.values():
            exporter.close()
        self._exporter_cache = {}

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, tb):
        force = exc_type is not None and isinstance(exc_type(), (FatalException, KeyboardInterrupt))
        self.close(force=force)

        if self.__state_need_close:
            self.state.__exit__(exc_type, exc_value, tb)
