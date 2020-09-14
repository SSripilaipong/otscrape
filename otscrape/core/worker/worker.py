import re
from urllib.parse import urlparse

from otscrape.core.base.worker import PoolWorkersBase
from otscrape.core.base.exporter import Exporter

from otscrape.core.exporter import JSONExporter

from .command import ScrapeCommand, ExportCommand


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


class Workers(PoolWorkersBase):
    def __init__(self, n_workers):
        super().__init__(n_workers=n_workers)

        self._exporter_cache = {}

    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        command = ScrapeCommand(self, buffer, buffer_size, buffer_timeout)
        return command.apply(page)

    def export(self, page, exporter, **kwargs):
        if not isinstance(exporter, Exporter):
            if exporter not in self._exporter_cache:
                exporter_obj = get_exporter(exporter, **kwargs)
                self._exporter_cache[exporter] = exporter_obj

                exporter_obj.open()

            exporter = self._exporter_cache[exporter]

        command = ExportCommand(self, exporter)
        return command.apply(page)

    def open(self):
        r = super().open()
        self._exporter_cache = {}
        return r

    def close(self):
        super().close()

        for exporter in self._exporter_cache.values():
            exporter.close()

        self._exporter_cache = {}
