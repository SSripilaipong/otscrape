from otscrape import Extractor


class Lambda(Extractor):
    def __init__(self, func, *, target=None, project=True, replace_error=None):
        super().__init__(target=target, project=project, replace_error=replace_error)
        self.func = func

    def extract(self, page, cache):
        x = page[self.target]
        return self.func(x)

    def __str__(self):
        return f'Lambda({self.func.__name__})'
