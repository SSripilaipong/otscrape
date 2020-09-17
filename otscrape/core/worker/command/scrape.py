from otscrape.core.base.worker import PoolCommand
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


class ScrapeCommand(PoolCommand):
    def __init__(self, buffer='FIFO', buffer_size=0, buffer_timeout=3.0):
        super().__init__()

        self.buffer = get_buffer(buffer, buffer_size, buffer_timeout)

    @staticmethod
    def calculate(page):
        page.do_load()
        return page.get_data()

    def callback(self, x):
        self.buffer.put(x)
        self.buffer.increase_task_counter()

    def finish(self, pages, *args, **kwargs):
        self.buffer.total_tasks = len(pages)
        return self.buffer
