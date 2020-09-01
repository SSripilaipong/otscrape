from otscrape.core.base.worker import ThreadWorkersBase
from otscrape.core.base.page import Page
from otscrape.core.base.buffer import Buffer

from otscrape.core.buffer import FIFOBufferBase, LIFOBufferBase


def get_buffer(type_, buffer_size, buffer_timeout):
    if isinstance(type_, Buffer):
        return type_
    elif isinstance(type_, str):
        type_ = type_.lower()
        if type_ == 'fifo':
            return FIFOBufferBase(buffer_size=buffer_size, buffer_timeout=buffer_timeout)
        elif type_ == 'lifo':
            return LIFOBufferBase(buffer_size=buffer_size, buffer_timeout=buffer_timeout)
        else:
            raise NotImplementedError(f'A buffer of type {type_} is not implemented.')
    else:
        raise TypeError(f'A buffer is expected to be of type str or Buffer. Got {type(type_)}.')


def ensure_page_iter(p):
    if isinstance(p, (list, tuple, set)):
        if all(isinstance(x, Page) for x in p):
            return p
        else:
            raise TypeError('All elements in the collection must be of type Page.')
    elif isinstance(p, Page):
        return [p]
    elif hasattr(p, '__iter__'):
        return p
    else:
        raise TypeError(f'Page of type {type(p)} is unexpected.')


class Workers(ThreadWorkersBase):
    def __init__(self, n_workers):
        super().__init__(n_workers=n_workers)

    def _scrape(self, page, buffer):
        page.fetch()
        buffer.put(page)

    def _export(self, page, exporter):
        page.fetch()
        exporter(page)

    def scrape(self, page, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        with self._count_lock:
            self._remain_tasks += 1

        pages = ensure_page_iter(page)
        buffer_obj = get_buffer(buffer, buffer_size, buffer_timeout)

        i = 0
        for i, page_ in enumerate(pages):
            kwargs = {
                'page': page_,
                'buffer': buffer_obj,
            }
            self.workers.apply_async(self._worker_call, (self._scrape, kwargs, buffer_obj.increase_task_counter))

        buffer_obj.total_tasks = i+1
        return buffer_obj

    def export(self, page, exporter):
        with self._count_lock:
            self._remain_tasks += 1

        pages = ensure_page_iter(page)

        for page_ in pages:
            kwargs = {
                'page': page_,
                'exporter': exporter,
            }
            self.workers.apply_async(self._worker_call, (self._export, kwargs))
