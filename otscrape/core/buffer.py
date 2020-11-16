import time
from threading import Lock
from queue import Queue, LifoQueue, Empty

from otscrape.core.base.buffer import Buffer, BufferRetryException


class QueueBufferBase(Buffer):
    def __init__(self, workers, buffer_size=0, buffer_timeout=3.0, total_tasks=None):
        super().__init__(workers, buffer_size, buffer_timeout, total_tasks)

        self._buffer = self.QueueClass(maxsize=self.buffer_size)

    @property
    def QueueClass(self):
        raise NotImplementedError()

    def empty(self):
        return self._buffer.empty()

    def get(self):
        try:
            return self._buffer.get(timeout=self.buffer_timeout)
        except Empty:
            raise BufferRetryException()

    def put(self, x):
        self._buffer.put(x)

    def task_done(self):
        self._buffer.task_done()


class FIFOBufferBase(QueueBufferBase):
    QueueClass = Queue


class LIFOBufferBase(QueueBufferBase):
    QueueClass = LifoQueue


class OrderedBuffer(Buffer):
    def __init__(self, workers, buffer_size=0, buffer_timeout=0.1, total_tasks=None):
        super().__init__(workers, buffer_size, buffer_timeout, total_tasks)

        self._buffer = dict()
        self._buffer_lock = Lock()
        self._buffer_index = 0

    def empty(self):
        with self._buffer_lock:
            return len(self._buffer) == 0

    def get(self):
        with self._buffer_lock:
            if self._buffer_index in self._buffer:
                return self._buffer[self._buffer_index]
            else:
                raise BufferRetryException()

    def put(self, x):
        with self._buffer_lock:
            self._buffer[x.order] = x

    def task_done(self):
        with self._buffer_lock:
            del self._buffer[self._buffer_index]
            self._buffer_index += 1

