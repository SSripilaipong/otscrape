import copy


class PathTokenizer:
    def check(self, path: str):
        raise NotImplementedError()

    def extract(self, path: str):
        raise NotImplementedError()

    def get_visitor(self, path: str):
        raise NotImplementedError()

    def tokenize(self, path: str):
        result = (None, None)
        if self.check(path):
            path, name = self.extract(path)
            visitor = self.get_visitor(name)
            result = (name, visitor)

        return path, result


class PathVisitor:
    def __init__(self, name, next_visitors=None, project=None, fields=None):
        self.name = name
        self.next_visitors = next_visitors or []
        self.project = project
        self.fields = fields or set()

    def visit(self, data):
        raise NotImplementedError()


class DeniedDataStructure(Exception):
    pass
