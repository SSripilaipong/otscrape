import traceback
import time
from copy import deepcopy
from threading import Lock
import requests

from otscrape.core.base.abstract import NoFailMixin
from otscrape.core.base.loader import Loader
from otscrape.core.base.exception import LoadingFailedException


class RequestLoaderBase(Loader):
    def __init__(self, method=None,  accept_status_codes=(200,), rate_limit='', max_retries=0, delay=0, **kwargs):
        super().__init__(rate_limit=rate_limit)

        self.method = method or 'GET'
        self.kwargs = kwargs or {}
        self.accept_status_codes = accept_status_codes
        self.max_retries = max_retries
        self.delay = delay

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if isinstance(v, Lock):
                setattr(result, k, v)  # share locks
            else:
                setattr(result, k, deepcopy(v, memo))
        return result

    def POST(self, **kwargs):
        result = deepcopy(self)
        result.method = 'POST'
        for k, v in kwargs.items():
            setattr(result, k, v)
        return result

    def GET(self, **kwargs):
        result = deepcopy(self)
        result.method = 'GET'
        for k, v in kwargs.items():
            setattr(result, k, v)
        return result

    def do_load(self, **kwargs):
        kwargs_update = dict(self.kwargs)
        kwargs_update.update(kwargs)

        assert 'url' in kwargs_update

        count = 0
        while True:
            try:
                resp = requests.request(self.method, **kwargs_update)
                if resp.status_code in self.accept_status_codes:
                    return resp
                resp.raise_for_status()
            except Exception as e:
                if count >= self.max_retries:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise LoadingFailedException(str(e))
            count += 1

            if self.delay:
                time.sleep(self.delay)


class SimpleRequestLoader(NoFailMixin, RequestLoaderBase):
    def __init__(self, method=None, accept_status_codes=(200,), max_retries=0, delay=0, replace_error=None, **kwargs):

        super().__init__(method=method, accept_status_codes=accept_status_codes,
                         max_retries=max_retries, delay=delay, **kwargs)
        self.replace_error = replace_error

    @property
    def _return_value_when_fail(self):
        return self.replace_error

    def on_error(self, *args, **kwargs):
        return super().on_error(*args, **kwargs)
