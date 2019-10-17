import typing
import abc
import random
import time
import re
import functools
import lxml.etree
import requests

from otscrape.exceptions import UnexpectedStatusCode


class Requester(abc.ABC):
    url_base = None
    delay = 0  # type: typing.Union[float, tuple]
    params = {}  # type: typing.Dict[str, typing.Any]
    ignore_exceptions = ()  # type: typing.Tuple[Exception]
    ignore_status_codes = ()  # type: typing.Tuple[int]
    max_retries = None  # type: int

    def __init__(self, url=None, url_format: typing.Dict[str, typing.Any] = None,
                 session: requests.Session = None, params: typing.Dict[str, typing.Any] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = url
        self._url_format = url_format or {}  # type: typing.Dict[str, typing.Any]
        self._session = session
        if params:
            self.params = self.__class__.params.copy()
            for key, value in params.items():
                self.params[key] = value

        self._etree = None
        self._source = None

    @property
    def method(self) -> str:
        raise NotImplementedError()

    def create_session(self):
        self._session = requests.Session()

    @property
    def session(self):
        if not self._session:
            self.create_session()
        return self._session

    @property
    def url_format(self):
        return self._url_format

    def make_request(self):
        retried = 0
        while True:
            try:
                url = self.url or self.url_base.format(**self.url_format)

                requester = self._session or requests
                resp = requester.request(self.method, url, **self.params)

                if resp.status_code == 200:
                    return resp
                if resp.status_code in self.ignore_status_codes:
                    if self.max_retries is not None and retried >= self.max_retries:
                        raise UnexpectedStatusCode(resp.status_code)
                else:
                    raise UnexpectedStatusCode(resp.status_code)

            except self.ignore_exceptions as e:
                if self.max_retries is not None and retried >= self.max_retries:
                    raise e

                retried += 1

            if self.delay:
                if isinstance(self.delay, tuple):
                    a, b = self.delay
                    t = random.random() * (b - a) + a
                    time.sleep(t)
                else:
                    time.sleep(self.delay)

    @property
    def source(self):
        if self._source is None:
            resp = self.make_request()  # type: requests.Response
            self._source = resp.text
        return self._source

    @property
    def etree(self):
        if self._etree is None:
            self._etree = lxml.etree.fromstring(self.source, parser=lxml.etree.HTMLParser())
        return self._etree

    @staticmethod
    def autoxpath(xpath):
        def dec(func):
            @functools.wraps(func)
            def wraps(self: Requester, *args, **kwargs):
                result = self.etree.xpath(xpath)
                return func(self, result, *args, **kwargs)
            return wraps
        return dec

    @staticmethod
    def automatch(pattern, flags=None):
        def dec(func):
            @functools.wraps(func)
            def wraps(self: Requester, *args, **kwargs):
                result = re.match(pattern, self.source, flags)
                return func(result, *args, **kwargs)
            return wraps
        return dec
