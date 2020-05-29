import requests
from otscrape.base.loader import Loader


class RequestLoader(Loader):
    def __init__(self, url, method, kwargs=None, accept_status_codes=(200,)):
        self.url = url
        self.method = method
        self.kwargs = kwargs or {}
        self.accept_status_codes = accept_status_codes

    def make_request(self):
        resp = requests.request(self.method, self.url, **self.kwargs)
        if resp.status_code in self.accept_status_codes:
            return resp
        resp.raise_for_status()

    def load(self):
        self.on_requesting()

        try:
            return self.make_request()
        except requests.RequestException as e:
            return self.on_request_error(e)
        finally:
            self.on_requested()

    def on_requesting(self):
        pass

    def on_requested(self):
        pass

    def on_request_error(self, exception):
        raise exception
