import time
from threading import Thread, Lock, Event
from queue import Queue

from otscrape.core.util import ensure_page_iter


class CommandExecutor:
    def __init__(self, pool):
        self.pool = pool

        self.lock = Lock()
        self.tasks = Queue()
        self.running = True

        self.push_event = Event()
        self.done_event = Event()

        self.curr_run_count = 0
        self.curr_run_lock = Lock()

        self.thread = Thread(target=self.loop)
        self.thread.start()

    def loop(self):
        self.push_event.wait()

        while self.running:
            target, page, callback = self.tasks.get()

            try:
                page.loader.on_loading()
            except AssertionError:
                self.tasks.put((target, page, callback))
                continue

            self._apply(target, (page,), callback)

            self.done_event.clear()
            if not self.pool_available:
                self.done_event.wait()

            self.push_event.clear()
            if not self.tasks.qsize():
                self.push_event.wait()

    @property
    def pool_available(self):
        with self.curr_run_lock:
            return self.curr_run_count < self.pool.n_workers

    def _apply(self, target, args, callback):
        with self.curr_run_lock:
            self.curr_run_count += 1

        self.pool.workers.apply_async(target, args=args, callback=callback)

    def execute(self, command, page, *args, **kwargs):
        pages = ensure_page_iter(page)
        callback = make_callback(command.callback, self.finish)

        pages_ = []
        for page_ in pages:
            self.pool.increase_task_counter()

            with self.lock:
                self.tasks.put((command.calculate, page_, callback))
            self.push_event.set()
            pages_.append(page_)

        return command.finish(pages_, *args, **kwargs)

    def finish(self):
        self.pool.decrease_task_counter()

        with self.curr_run_lock:
            self.curr_run_count -= 1

        self.done_event.set()


def make_callback(callback, finish):
    def f(x):
        callback(x)
        finish()

    return f
