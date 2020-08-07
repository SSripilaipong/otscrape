from otscrape.base.mixins import NoFailMixin


class ExtractorBase:
    is_extractor = True

    def __init__(self, target=None, project=True):
        self.target = target or 'raw'
        self.do_project = project

    def _extract(self, page):
        try:
            return self.extract(page)
        except Exception as e:
            return self.on_extract_error(e)

    def _on_extract_error(self, exception):
        return self.on_extract_error(exception)

    def on_extract_error(self, exception):
        raise exception

    def extract(self, page):
        raise NotImplementedError()


class Extractor(NoFailMixin, ExtractorBase):
    def __init__(self, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project)
        self.replace_error = replace_error

    @property
    def _return_value_when_fail(self):
        return self.replace_error

    def on_extract_error(self, *args, **kwargs):
        return self.on_error(*args, **kwargs)
