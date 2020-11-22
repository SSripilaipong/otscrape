import traceback
import re
from urllib.parse import urlparse

from otscrape.core.base.page import PageBase
from otscrape.core.base.worker import PoolCommand
from otscrape.core.base.exporter import Exporter
from otscrape.core.base.exception import LoadingFailedException

from otscrape.core.exporter import JSONExporter


def get_request_exporter(method, url):
    pass


def check_request_exporter(exporter):
    request_match = re.match(r'^(?P<method>get |post |put |delete )(?P<url>https?://.*)', exporter.lower())
    if request_match:
        match = request_match.groupdict()
        return get_request_exporter(method=match['method'], url=match['url'])
    return


def get_local_file_exporter(path):
    if path.lower().endswith('.json'):
        return JSONExporter(path, parallel=True)
    else:
        raise NotImplementedError()


def check_file_exporter(exporter):
    o = urlparse(exporter)
    if o.scheme.lower() in ('', 'file') and o.netloc.lower() in ('', 'localhost') and o.path:  # local file
        return get_local_file_exporter(o.path)
    return


def get_exporter(exporter, **kwargs):
    if isinstance(exporter, Exporter):
        return exporter

    elif isinstance(exporter, str):
        e = (check_file_exporter(exporter)
             or check_request_exporter(exporter))
        if e:
            return e
        else:
            raise NotImplementedError()

    else:
        raise NotImplementedError()


class ExportCommand(PoolCommand):
    def __init__(self, exporter: Exporter, exporter_cache, state=None, **kwargs):
        super().__init__(state=state)

        if not isinstance(exporter, Exporter):
            if exporter not in exporter_cache:
                exporter_obj = get_exporter(exporter, **kwargs)
                exporter_cache[exporter] = exporter_obj

                exporter_obj.open()

            exporter = exporter_cache[exporter]

        self.exporter = exporter

    @staticmethod
    def calculate(page: PageBase):
        page.do_load()
        page.get_data()
        page.prune()
        return page

    def callback(self, result):
        exception = result.exception
        if not exception:
            self.exporter(result.page)

        if result.state:
            result.state.try_complete()

    def drop_callback(self, result):
        super().drop_callback(result)

        if result.state:
            result.state.try_complete()
