from copy import deepcopy
import requests

from otscrape.core.base.mixins import NoFailMixin
from otscrape.core.base.loader import Loader


class RequestLoaderBase(Loader):
    def __init__(self, method=None, accept_status_codes=(200,), **kwargs):
        super().__init__()

        self.method = method or 'GET'
        self.kwargs = kwargs or {}
        self.accept_status_codes = accept_status_codes

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def post(self, **kwargs):
        result = deepcopy(self)
        result.method = 'POST'
        for k, v in kwargs.items():
            setattr(result, k, v)
        return result

    def get(self, **kwargs):
        result = deepcopy(self)
        result.method = 'GET'
        for k, v in kwargs.items():
            setattr(result, k, v)
        return result

    def make_request(self, url, **kwargs):
        kwargs_update = dict(self.kwargs)
        kwargs_update.update(kwargs)
        kwargs_update['url'] = url

        resp = requests.request(self.method, **kwargs_update)
        if resp.status_code in self.accept_status_codes:
            return resp
        resp.raise_for_status()

    def __call__(self, url, **kwargs):
        self.on_requesting()

        try:
            return self.make_request(url, **kwargs)
        except Exception as e:
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


class SimpleRequestLoader(NoFailMixin, RequestLoaderBase):
    def __init__(self, method=None, accept_status_codes=(200,), replace_error=None, **kwargs):
        super().__init__(method=method, accept_status_codes=accept_status_codes, **kwargs)
        self.replace_error = replace_error

    @property
    def _return_value_when_fail(self):
        return self.replace_error

    def on_request_error(self, *args, **kwargs):
        return self.on_error(*args, **kwargs)
