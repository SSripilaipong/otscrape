from otscrape.core.base.state import MemoryState

from .page import PageBase


class PageWrapper:
    def __init__(self, page, state):
        self.page = page  # type: PageBase
        self.state = state  # type: MemoryState

    def complete(self):
        self.state.complete()
