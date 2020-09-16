class Loader:
    def check_available(self):
        return True

    def get_available_time(self):
        return 0

    def __call__(self, *args, **kwargs):
        self.do_on_loading()

        try:
            return self.do_load(*args, **kwargs)
        except Exception as e:
            return self.on_load_error(e)
        finally:
            self._on_loaded()

    def do_load(self, *args, **kwargs):
        raise NotImplementedError()

    def do_on_loading(self):
        return self.on_loading()

    def _on_loaded(self):
        return self.on_loaded()

    def _on_load_error(self, exception):
        return self.on_load_error(exception)

    def on_loading(self):
        pass

    def on_loaded(self):
        pass

    def on_load_error(self, exception):
        raise exception
