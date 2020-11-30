import traceback
import multiprocessing
from multiprocessing import Pool, Value, Event

from otscrape.core.base.wrapper import PageWrapper
from otscrape.core.base.exception import PoolWorkerFailedException
from otscrape.core.base.exception import DropCommandException
from otscrape.core.base import share


def ensure_n_workers(n_workers):
    if n_workers is None:
        if multiprocessing.cpu_count() == 1:
            n_workers = 1
        else:
            n_workers = -1

    if n_workers < 0:
        n_workers = multiprocessing.cpu_count() - n_workers

    assert isinstance(n_workers, int) and 0 < n_workers

    return n_workers


def pool_init():
    share.is_worker = True


class PoolManager:
    def __init__(self, n_workers=None):
        self.n_workers = ensure_n_workers(n_workers)

        self.ready = False
        self.workers = None  # type: Pool

        self._remain_tasks = None
        self._work_done_event = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def open(self):
        assert not self.ready

        self._remain_tasks = Value('i', 0)
        self._work_done_event = Event()
        self.workers = Pool(self.n_workers, initializer=pool_init)
        self.ready = True

        return self

    def close(self, force=False):
        assert self.ready

        if not force:
            self._work_done_event.clear()
            while self.count_remaining_tasks() > 0:
                self._work_done_event.wait()
                self._work_done_event.clear()

        self.workers.close()
        self.workers.join()

    def count_remaining_tasks(self):
        with self._remain_tasks.get_lock():
            return self._remain_tasks.value

    def increase_task_counter(self):
        with self._remain_tasks.get_lock():
            self._remain_tasks.value += 1

    def decrease_task_counter(self):
        with self._remain_tasks.get_lock():
            self._remain_tasks.value -= 1

        self._work_done_event.set()


class PoolCommand:
    def __init__(self, state=None):
        self.state = state

    @staticmethod
    def prepare(page):
        page.loader.do_on_loading()

    def validate_input(self, page):
        return

    @staticmethod
    def calculate(page):
        raise NotImplementedError()

    def make_result(self, order, page, exception):
        ss = self.state.substate(page) if self.state else None
        result = PageWrapper(page, order, state=ss, exception=exception)
        return result

    def do_callback(self, result):
        page = result.page
        exception = result.exception
        if exception:
            if isinstance(exception, (DropCommandException,)):
                self.drop_callback(result)
                return

            traceback.print_exception(type(exception), exception, exception.__traceback__)

            try:
                message = f'Page {page} (key: {page["key"]!r}) was not processed successfully.'
            except KeyError:
                message = f'Page {page} was not processed successfully.'
            exception = PoolWorkerFailedException(message)
            traceback.print_exception(type(exception), exception, None)

        self.callback(result)

    def drop_callback(self, page_wrapper):
        pass

    def callback(self, page_wrapper):
        pass

    def finish(self, pages, *args, **kwargs):
        return

    def create_task(self, page, order):
        task = PoolTask(self, page, order)
        return task


class PoolTask:
    def __init__(self, command: PoolCommand, page, order):
        self.page = page
        self.order = order

        command.validate_input(self.page)

        self.calculation = PoolTaskCalculation(self.order, command.calculate).calculation
        self.command_prepare = command.prepare
        self.callback = command.do_callback
        self.drop_callback = command.drop_callback
        self.make_result = command.make_result

    def prepare(self):
        return self.command_prepare(self.page)


class PoolTaskCalculation:
    def __init__(self, order, command_calculate):
        self.order = order
        self.command_calculate = command_calculate

    def calculation(self, x):
        exception = None

        try:
            x = self.command_calculate(x)
        except Exception as e:
            exception = e

        return self.order, x, exception
