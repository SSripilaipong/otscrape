from threading import Thread, Lock
from threading import Event
from queue import Queue, Empty

from otscrape.core.base.exception import (DropCommandException,
                                          LoaderNotAvailableException)
from otscrape.core.util import ensure_page_iter

from .pool import PoolManager, PoolCommand


class TaskManager(Thread):
    def __init__(self, executor):
        self.executor = executor  # type: CommandExecutor
        self.running = True

        super().__init__()

    def run(self):
        self.executor.wait_task_exist_or_end()

        while self.running or self.executor.n_waiting_tasks:
            try:
                task = self.executor.get_task(timeout=3.0)
            except Empty:
                continue

            try:
                task.prepare()
            except DropCommandException as e:
                callback = self.executor.make_callback(task.drop_callback, task.make_result)
                callback((task.order, task.page, e))
                continue
            except LoaderNotAvailableException:
                self.executor.put_task(task)
                continue

            self.executor.execute_task(task)

            self.executor.wait_pool()
            self.executor.wait_task_exist_or_end()

    def close(self):
        self.running = False
        self.join()


class CommandExecutor:
    def __init__(self, n_workers=None):
        self.pool = PoolManager(n_workers=n_workers)

        self.tasks = Queue()

        self.curr_run_count = 0
        self.curr_run_lock = Lock()

        self.push_event = Event()
        self.done_event = Event()

        self.running = False
        self.task_manager = TaskManager(self)

    def open(self):
        self.pool.open()
        self.task_manager.start()

        self.running = True

    def close(self, force=False):
        self._stop()

        self.task_manager.close()
        self.pool.close(force=force)

        self.running = False

    def _stop(self):
        self.running = False
        self.push_event.set()

    def get_task(self, timeout=3.0):
        return self.tasks.get(timeout=timeout)

    def put_task(self, task):
        self.tasks.put(task)

    def execute_task(self, task):
        self._apply(task.calculation, (task.page,), self.make_callback(task.callback, task.make_result))

    def wait_pool(self):
        self.done_event.clear()
        if not self.pool_available:
            self.done_event.wait()

    def wait_task_exist_or_end(self):
        if not self.running:
            return

        self.push_event.clear()
        if not self.tasks.qsize():
            self.push_event.wait()

    @property
    def n_running_tasks(self):
        with self.curr_run_lock:
            return self.curr_run_count

    @property
    def n_waiting_tasks(self):
        return self.tasks.qsize()

    @property
    def pool_available(self):
        with self.curr_run_lock:
            return self.curr_run_count < self.pool.n_workers

    def _apply(self, target, args, callback):
        with self.curr_run_lock:
            self.curr_run_count += 1

        self.pool.workers.apply_async(target, args=args, callback=callback)

        # a = self.pool.workers.apply(target, args=args)
        # callback(a)

    def execute(self, command: PoolCommand, page, state=None, *args, **kwargs):
        pages = ensure_page_iter(page)

        pages_ = []
        if state:
            state.hold()
        for order, page_ in enumerate(pages):
            if state:
                if state.is_complete(name=page_):
                    continue

                _ = state.substate(page_)

            self.pool.increase_task_counter()

            task = command.create_task(page_, order=order)

            self.tasks.put(task)

            self.push_event.set()
            pages_.append(page_)

        if state:
            state.release()

        return command.finish(pages_, *args, **kwargs)

    def finish(self):
        self.pool.decrease_task_counter()

        with self.curr_run_lock:
            self.curr_run_count -= 1

        self.done_event.set()

    def make_callback(self, callback, make_result):
        def f(args):
            result = make_result(*args)
            callback(result)
            self.finish()

        return f
