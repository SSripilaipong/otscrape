import requests
from otscrape.base.loader import Loader


class SimpleRequestLoader(Loader):
    def __init__(self, kwargs=None, accept_status_codes=(200,)):
        self.kwargs = kwargs or {}
        self.accept_status_codes = accept_status_codes

    def _get_kwargs(self):
        kwargs = {
            'kwargs': dict(**self.kwargs, method='GET'),
            'accept_status_codes': self.accept_status_codes,
        }
        return kwargs

    def post(self):
        kwargs = self._get_kwargs()
        kwargs.update({'method': 'POST'})
        return SimpleRequestLoader(**kwargs)

    def get(self):
        kwargs = self._get_kwargs()
        kwargs.update({'method': 'GET'})
        return SimpleRequestLoader(**kwargs)

    def make_request(self, url, **kwargs):
        kwargs_update = dict(self.kwargs)
        kwargs_update.update(kwargs)
        kwargs_update['method'] = kwargs_update.get('method', 'GET')
        kwargs_update['url'] = url

        resp = requests.request(**kwargs_update)
        if resp.status_code in self.accept_status_codes:
            return resp
        resp.raise_for_status()

    def __call__(self, url, **kwargs):
        self.on_requesting()

        try:
            return self.make_request(url, **kwargs)
        except requests.RequestException as e:
            return self.on_request_error(e)
        finally:
            self.on_requested()

    def _on_requesting(self):
        return self.on_requesting()

    def _on_requested(self):
        return self.on_requested()

    def _on_request_error(self, exception):
        return self.on_request_error(exception)

    def on_requesting(self):
        pass

    def on_requested(self):
        pass

    def on_request_error(self, exception):
        raise exception
