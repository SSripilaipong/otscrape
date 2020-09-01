from queue import Queue, LifoQueue, Empty

from otscrape.core.base.buffer import Buffer, BufferRetryException


class QueueBufferBase(Buffer):
    def __init__(self, buffer_size=0, buffer_timeout=3.0, total_tasks=None):
        super().__init__(buffer_size, buffer_timeout, total_tasks)

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
