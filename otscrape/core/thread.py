import time
import threading
import queue
import typing


class AutoScaleThread:
    def __init__(self, func=None, min_worker_threads=1, max_worker_threads=8, qt_ratio=2, worker_timeout=5):
        self._func = func  # type: typing.Optional[typing.Callable]
        self.min_worker_threads = min_worker_threads
        self.max_worker_threads = max_worker_threads
        self.qt_ratio = qt_ratio
        self.worker_timeout = worker_timeout

        self._control_thread = None

        self._worker_threads = []  # type: typing.List[threading.Thread]
        self._worker_threads_lock = threading.Lock()

        self._input_queue = queue.Queue()

        self._running = False

    def is_running(self):
        return self._running

    def _worker_func(self):
        while True:
            try:
                input_data = self._input_queue.get(timeout=self.worker_timeout)
            except queue.Empty:
                break

            try:
                output_data = self._func(input_data)
            except Exception as e:
                self._handle_process_exception(input_data, e)
                continue

            try:
                self.export(output_data)
            except Exception as e:
                self._handle_export_exception(input_data, output_data, e)
                continue

    def _spawn_thread(self):
        thread = threading.Thread(target=self._worker_func)
        thread.daemon = True
        thread.start()

        return thread

    def _control_thread(self):
        while self._running:
            with self._worker_threads_lock.acquire():
                self._worker_threads = [thread for thread in self._worker_threads if thread.is_alive()]

                if self._input_queue.qsize()/len(self._worker_threads) > self.qt_ratio:
                    thread = self._spawn_thread()
                    self._worker_threads.append(thread)

                while len(self._worker_threads) < self.min_worker_threads:
                    self._spawn_thread()
                    self._worker_threads.append(thread)

            time.sleep(1)

    def _spawn_control_thread(self):
        assert self._control_thread is None

        self._control_thread = threading.Thread(target=self._control_thread)
        self._control_thread.daemon = True
        self._control_thread.start()

    def start(self):
        if not self._running:
            self._spawn_control_thread()
            self._running = True

    def stop(self):
        self._running = False

    def feed(self, data):
        self._input_queue.put(data)

    def _handle_process_exception(self, input_data, exception):
        pass

    def _handle_export_exception(self, input_data, output_data, exception):
        pass

    def export(self, data):
        pass
