import traceback


class Extractor:
    is_extractor = True

    def __init__(self, target=None, project=True, replace_error=None):
        self.target = target or 'raw'
        self.do_project = project
        self.replace_error = replace_error

    def _extract(self, page):
        try:
            return self.extract(page)
        except:
            traceback.print_stack()

            value = self.replace_error
            if callable(value):
                value = value()
            return value

    def extract(self, page):
        raise NotImplementedError()
