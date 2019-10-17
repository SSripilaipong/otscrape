import typing
from otscrape.base import Page, ListingPage, ContentPage
from otscrape.base.page import PageReference


class Scraper:
    def __init__(self, root_page):
        self.root_page = root_page  # type: ListingPage
        self._page_stack = []  # type: typing.List[typing.Iterator]

    def __iter__(self):
        self._page_stack = [iter(self.root_page)]
        return self

    def __next__(self):
        while True:
            if not self._page_stack:
                raise StopIteration()

            try:
                child = next(self._page_stack[-1])  # type: Page
            except StopIteration:
                self._page_stack = self._page_stack[:-1]
                continue

            return_node = child.backtrack(child.reference)  # type: PageReference
            if return_node:
                last_id = id(child)
                while self._page_stack and return_node.object_id != last_id:
                    last_id = id(self._page_stack[-1])
                    self._page_stack = self._page_stack[:-1]

            else:
                if isinstance(child, ContentPage):
                    return child.data
                elif isinstance(child, ListingPage):
                    self._page_stack.append(iter(child))
                else:
                    raise TypeError(f'ListingPage returned an object of type {type(child)}')
