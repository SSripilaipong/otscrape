from otscrape.core.base.state import MemoryState

from .page import PageBase


class PageWrapper:
    def __init__(self, page, order, state):
        self.page = page  # type: PageBase
        self.order = order  # type: int
        self.state = state  # type: MemoryState

    def complete(self):
        self.state.complete()
