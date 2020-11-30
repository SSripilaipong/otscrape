import traceback


class NoFailMixin:
    _return_value_when_fail = None

    def on_error(self, exception, message=None):
        try:
            if hasattr(super(), 'on_error'):
                super().on_error(exception)
        except Exception as e:
            return self.__handle_error(e, message)

        return self.__handle_error(exception, message)

    def __handle_error(self, exception, message=None):
        traceback.print_exception(type(exception), exception, exception.__traceback__)
        if message:
            exception = exception.__class__(message).with_traceback(exception.__traceback__)
        traceback.print_exception(type(exception), exception, None)

        value = self._return_value_when_fail
        if callable(value):
            value = value()
        return value
