from otscrape.core.base.state import MemoryState
from otscrape.core.base.exception import StateOnWaitingException
from otscrape.core.base.worker import WorkersBase

from .command import ScrapeCommand, ExportCommand


class StatefulList:
    def __init__(self, workers):
        self.workers = workers

        self._list = []
        self._state_list = []

        self.state = self.workers.current_state.substate(suffix='list')  # type: MemoryState

    def append(self, x):
        ss = self.workers.current_state.substate(x)
        self.state.wait_for(ss)

        self._list.append(x)
        self._state_list.append(ss)

    def __iter__(self):
        for i, x in enumerate(self.workers.iter(self._list)):
            ss = self._state_list[i]
            ss.wait_for(self.workers.current_state)

            yield x

        self._list = []
        self._state_list = []


class Workers(WorkersBase):
    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        state = self.current_state.substate(suffix='scrape')  # type: MemoryState
        command = ScrapeCommand(self, buffer, buffer_size, buffer_timeout, state=state)
        return self._executor.execute(command, page, state=state)

    def export(self, page, exporter, **kwargs):
        state = self.current_state.substate(suffix='export')  # type: MemoryState
        command = ExportCommand(exporter, self._exporter_cache, state=state, **kwargs)
        return self._executor.execute(command, page)

    def list(self, elements=None):
        elements = elements or ()
        x = StatefulList(workers=self)
        for e in elements:
            x.append(e)
        return x
