import requests
from otscrape.base.loader import Loader


class RequestLoader(Loader):
    def __init__(self, method, default_kwargs=None, accept_status_codes=(200,)):
        self.method = method
        self.default_kwargs = default_kwargs or {}
        self.accept_status_codes = accept_status_codes

    def make_request(self, url, **kwargs):
        _kwargs = dict(**self.default_kwargs, **kwargs)

        resp = requests.request(self.method, url, **_kwargs)
        if resp.status_code in self.accept_status_codes:
            return resp
        resp.raise_for_status()

    def load(self, url, **kwargs):
        self.on_requesting(url, **kwargs)

        try:
            return self.make_request(url, **kwargs)
        except requests.RequestException as e:
            return self.on_request_error(e, url, **kwargs)
        finally:
            self.on_requested(url, **kwargs)

    def on_requesting(self, url, **kwargs):
        pass

    def on_requested(self, url, **kwargs):
        pass

    def on_request_error(self, exception, url, **kwargs):
        raise exception
