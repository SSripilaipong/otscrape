from .abstract import WillFail


class Loader(WillFail):
    def check_available(self):
        return True

    def get_available_time(self):
        return 0

    def __call__(self, *args, **kwargs):
        self.do_on_loading()

        return self._run_will_fail(*args, **kwargs)

    def _run(self, *args, **kwargs):
        try:
            return self.do_load(*args, **kwargs)
        finally:
            self._on_loaded()

    def do_load(self, *args, **kwargs):
        raise NotImplementedError()

    def do_on_loading(self):
        return self.on_loading()

    def _on_loaded(self):
        return self.on_loaded()

    def on_loading(self):
        pass

    def on_loaded(self):
        pass
