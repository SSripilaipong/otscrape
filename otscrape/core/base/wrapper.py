from otscrape.core.base.state import MemoryState

from .page import PageBase


class PageWrapper:
    def __init__(self, page, order, state, exception=None):
        self.page = page  # type: PageBase
        self.order = order  # type: int
        self.state = state  # type: MemoryState
        self.exception = exception  # type: Exception

    def complete(self):
        self.state.complete()
