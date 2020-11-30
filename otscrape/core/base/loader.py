import datetime
from collections import deque
from threading import Lock

from .exception import LoaderNotAvailableException
from .abstract import WillFail


class RateLimitConstraint:
    def __init__(self, rate_limit=''):
        self.rate_limit = rate_limit
        self.rate_limit_count, self.rate_limit_second = (map(float, rate_limit.split('/'))
                                                         if rate_limit else (float('inf'), float('inf')))
        self.timestamp_queue = deque()

    def check_available(self):
        if not self.rate_limit:
            return True

        if not self.timestamp_queue:
            return True

        now = datetime.datetime.now().timestamp()

        while self.timestamp_queue and now - self.timestamp_queue[0] > self.rate_limit_second:
            self.timestamp_queue.popleft()

        count = len(self.timestamp_queue)
        return count < self.rate_limit_count

    def on_available(self):
        timestamp = datetime.datetime.now().timestamp()
        self.timestamp_queue.append(timestamp)

    def get_available_time(self):
        if self.check_available():
            return 0

        first = self.timestamp_queue[0]

        now = datetime.datetime.now().timestamp()

        return max(self.rate_limit_second - (now - first), 0)


class Loader(WillFail):
    def __init__(self, rate_limit=''):
        super().__init__()

        self.rate_limit = rate_limit
        self.constraints = []

        if rate_limit:
            self.constraints.append(RateLimitConstraint(rate_limit=rate_limit))

        self.constraint_lock = Lock()

    def __getstate__(self):
        state = dict(self.__dict__)
        del state['constraint_lock']  # no need when processing
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__['constraint_lock'] = None

    def _check_available_no_lock(self):
        for constraint in self.constraints:
            if not constraint.check_available():
                return False
        return True

    def check_available(self, lock=True):
        if lock:
            with self.constraint_lock:
                return self._check_available_no_lock()
        return self._check_available_no_lock()

    def on_available(self):
        for constraint in self.constraints:
            constraint.on_available()

    def __call__(self, *args, **kwargs):
        self.do_on_loading()

        return self._run_will_fail(*args, **kwargs)

    def _run(self, *args, **kwargs):
        try:
            return self.do_load(*args, **kwargs)
        finally:
            self._on_loaded()

    def get_available_time(self):
        if self.constraints:
            with self.constraint_lock:
                return max(constraint.get_available_time() for constraint in self.constraints)
        return 0

    def do_load(self, *args, **kwargs):
        raise NotImplementedError()

    def do_on_loading(self):
        return self.on_loading()

    def _on_loaded(self):
        return self.on_loaded()

    def on_loading(self):
        with self.constraint_lock:
            if not self.check_available(lock=False):
                raise LoaderNotAvailableException()

            self.on_available()

    def on_loaded(self):
        pass
