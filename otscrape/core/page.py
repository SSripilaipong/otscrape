import typing
import abc

from otscrape.base import ContentPage, ListingPage, Page, Requester


class ItemListingPage(ListingPage, abc.ABC):
    state_init = {'index': 0}
    items = []

    def get_children(self, state) -> typing.List[Page]:
        return [self.get_item(self.items[state['index']])]

    def get_item(self, item) -> Page:
        raise NotImplementedError()

    def update_state(self, state) -> dict:
        return {'index': state['index'] + 1}

    def check_stop(self, state) -> bool:
        return state['index'] >= len(self.items)


class ListingRequester(Requester, ListingPage, abc.ABC):
    def on_update(self, old, new):
        super().on_update(old, new)

        self._source = None
        self._etree = None

    @property
    def url_format(self):
        url_format = self._url_format.copy()
        url_format.update(self._state)
        return url_format


class ContentRequester(Requester, ContentPage, abc.ABC):
    pass
