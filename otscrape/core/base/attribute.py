from otscrape.core.base.mixins import NoFailMixin


class AttributeBase:
    def __init__(self, target=None, project=True):
        self.target = target or 'raw'
        self.do_project = project

    def __call__(self, page):
        try:
            return self.extract(page)
        except Exception as e:
            return self._on_extract_error(e)

    def _on_extract_error(self, exception):
        return self.on_extract_error(exception)

    def on_extract_error(self, exception):
        raise exception

    def extract(self, page):
        raise NotImplementedError()


class Attribute(NoFailMixin, AttributeBase):
    def __init__(self, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.replace_error = replace_error

    @property
    def _return_value_when_fail(self):
        return self.replace_error

    def on_extract_error(self, *args, **kwargs):
        message = f'An error occurred while applying {self.__class__.__name__}() to attribute "{self.target}".'
        return self.on_error(*args, message=message, **kwargs)


def attribute(func=None, *, project=True, replace_error=None):
    if func:
        x = Attribute(project=project, replace_error=replace_error)
        x.extract = func
        return x

    def func_(f):
        x_ = Attribute(project=project, replace_error=replace_error)
        x_.extract = f
        return x_
    return func_
