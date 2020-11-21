import queue
from multiprocessing import Queue, Value, TimeoutError

from otscrape.core.base.exception import LoadingFailedException
from otscrape.core.base.loader import Loader


code_mapper = [
    ('B', 1),
    ('I', 2),
    ('L', 4),
    ('Q', 8),
]


class LineLoader(Loader):
    def __init__(self, filename, rate_limit='', batch_size=None, **kwargs):
        super().__init__(rate_limit=rate_limit)

        self.filename = filename
        self.batch_size = batch_size

        self.total_lines = sum(1 for _ in open(filename))

        for code, size in code_mapper:
            if self.total_lines <= 2**(size*8) - 1:
                type_code = code
                break
        else:
            raise NotImplementedError(f'File {self.filename} is too large, has too many lines ({self.total_lines}). '
                                      f'The limit is {2**(code_mapper[-1][1]*8)-1} lines.')
        self.read_lines = Value(type_code, 0)

        self.line_queue = Queue()

    def do_load(self):
        while True:
            with self.read_lines.get_lock():
                nl = self.read_lines.value

            if nl == self.total_lines:
                raise LoadingFailedException('All lines are already read.')

            try:
                data = self.line_queue.get(timeout=3)
                self.line_queue.task_done()
                return data
            except queue.Empty:
                continue
