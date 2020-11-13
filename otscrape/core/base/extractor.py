from .abstract import WillFail, NoFailMixin


class ExtractorBase(WillFail):
    def __init__(self, target=None, project=True):
        self.target = target or 'raw'
        self.do_project = project

    def __call__(self, page):
        return self._run_will_fail(page)

    def _run(self, page):
        return self.extract(page)

    def extract(self, page):
        raise NotImplementedError()


class Extractor(NoFailMixin, ExtractorBase):
    def __init__(self, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.replace_error = replace_error

    @property
    def _return_value_when_fail(self):
        return self.replace_error

    def on_error(self, *args, **kwargs):
        message = f'An error occurred while applying {self.__class__.__name__}() to attribute "{self.target}".'
        return super().on_error(*args, message=message, **kwargs)


def extractor(func=None, *, project=True, replace_error=None):
    if func:
        x = Extractor(project=project, replace_error=replace_error)
        x.extract = func
        return x

    def func_(f):
        x_ = Extractor(project=project, replace_error=replace_error)
        x_.extract = f
        return x_
    return func_


class Attribute(Extractor):
    pass
