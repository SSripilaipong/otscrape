class WillFail:
    def _run(self, *args, **kwargs):
        raise NotImplementedError()

    def _run_will_fail(self, *args, **kwargs):
        try:
            return self._run(*args, **kwargs)
        except Exception as e:
            return self._on_error(e)

    def _on_error(self, exception):
        return self.on_error(exception)

    def on_error(self, exception):
        raise exception
