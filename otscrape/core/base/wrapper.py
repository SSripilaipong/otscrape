from typing import List

from otscrape.core.base.state import MemoryState

from .page import Page


class PageWrapper:
    def __init__(self, page, state):
        self.page = page  # type: Page
        self.state = state  # type: MemoryState

    def complete(self):
        self.state.complete()
