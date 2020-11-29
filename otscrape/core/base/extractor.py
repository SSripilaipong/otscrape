from inspect import signature
from .abstract import WillFail, NoFailMixin


class ExtractorBase(WillFail):
    def __init__(self, target=None, project=True):
        self.target = target or 'raw'
        self.do_project = project

    def __call__(self, page):
        return self._run_will_fail(page)

    def _run(self, page):
        return self.extract(page, getattr(page, '_cached', {}))

    def extract(self, page, cache):
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
    def dec(f):
        x = Extractor(project=project, replace_error=replace_error)

        sig = signature(f)
        params = sig.parameters
        if len(params) == 1:
            x.extract = lambda page, _: f(page)
        elif len(params) > 1:
            x.extract = f
        else:
            raise TypeError(f'Extractor method must have at least one parameter.')

        return x

    if func:
        return dec(func)
    return dec


class Attribute(Extractor):
    pass
