import time
import datetime
from copy import deepcopy
from collections import deque
import requests
from threading import Lock

from otscrape.core.base.abstract import NoFailMixin
from otscrape.core.base.loader import Loader


class RequestLoaderBase(Loader):
    def __init__(self, method=None,  accept_status_codes=(200,), rate_limit='', max_retries=0, delay=0, **kwargs):
        super().__init__()

        self.method = method or 'GET'
        self.kwargs = kwargs or {}
        self.accept_status_codes = accept_status_codes
        self.rate_limit = rate_limit
        self.rate_limit_count, self.rate_limit_second = (map(float, rate_limit.split('/'))
                                                         if rate_limit else (float('inf'), float('inf')))
        self.max_retries = max_retries
        self.delay = delay

        self.lock = Lock()
        self.timestamp_queue = deque()

    def _check_available_no_lock(self):
        if not self.timestamp_queue:
            return True

        now = datetime.datetime.now().timestamp()

        while self.timestamp_queue and now - self.timestamp_queue[0] > self.rate_limit_second:
            self.timestamp_queue.popleft()

        count = len(self.timestamp_queue)
        return count < self.rate_limit_count

    def check_available(self, lock=True):
        if not self.rate_limit:
            return True

        if lock:
            with self.lock:
                return self._check_available_no_lock()
        return self._check_available_no_lock()

    def get_available_time(self):
        if self.check_available():
            return 0

        with self.lock:
            first = self.timestamp_queue[0]

        now = datetime.datetime.now().timestamp()

        return max(self.rate_limit_second - (now - first), 0)

    def on_loading(self):
        with self.lock:
            assert self.check_available(lock=False)

            timestamp = datetime.datetime.now().timestamp()
            self.timestamp_queue.append(timestamp)

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

    def do_load(self, url, **kwargs):
        kwargs_update = dict(self.kwargs)
        kwargs_update.update(kwargs)
        kwargs_update['url'] = url

        count = 0
        while True:
            try:
                resp = requests.request(self.method, **kwargs_update)
                if resp.status_code in self.accept_status_codes:
                    return resp
                resp.raise_for_status()
            except Exception as e:
                if count >= self.max_retries:
                    raise e
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

    def on_load_error(self, *args, **kwargs):
        return self.on_error(*args, **kwargs)
