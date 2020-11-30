from otscrape.core.base.worker import PoolCommand
from otscrape.core.base.buffer import Buffer

from otscrape.core.buffer import FIFOBufferBase, LIFOBufferBase, OrderedBuffer


def get_buffer(workers, type_, buffer_size, buffer_timeout):
    if isinstance(type_, Buffer):
        return type_
    elif isinstance(type_, str):
        type_ = type_.lower()
        if type_ == 'fifo':
            return FIFOBufferBase(workers, buffer_size=buffer_size, buffer_timeout=buffer_timeout)
        elif type_ == 'lifo':
            return LIFOBufferBase(workers, buffer_size=buffer_size, buffer_timeout=buffer_timeout)
        elif type_ == 'order':
            return OrderedBuffer(workers, buffer_size=buffer_size, buffer_timeout=buffer_timeout)
        else:
            raise NotImplementedError(f'A buffer of type {type_} is not implemented.')
    else:
        raise TypeError(f'A buffer is expected to be of type str or Buffer. Got {type(type_)}.')


class ScrapeCommand(PoolCommand):
    def __init__(self, workers, buffer='FIFO', buffer_size=0, buffer_timeout=3.0, state=None):
        super().__init__(state=state)

        self.buffer = get_buffer(workers, buffer, buffer_size, buffer_timeout)

    @staticmethod
    def calculate(page):
        page.do_load()
        page.get_data()
        page.prune()
        return page

    def callback(self, result):
        self.buffer.put(result)  # let the buffer handle if an exception exists
        self.buffer.increase_task_counter()

    def drop_callback(self, result):
        self.buffer.increase_task_counter()
        if result.state:
            result.state.try_complete()

    def finish(self, pages, *args, **kwargs):
        super().finish(pages, *args, **kwargs)

        self.buffer.total_tasks = len(pages)
        return self.buffer
