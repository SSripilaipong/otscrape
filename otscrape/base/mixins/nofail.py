import traceback


class NoFailMixin:
    _return_value_when_fail = None

    def on_error(self, exception):
        try:
            if hasattr(super(), 'on_error'):
                super().on_error(exception)
            raise exception
        except:
            traceback.print_exc()

            value = self._return_value_when_fail
            if callable(value):
                value = value()
            return value
