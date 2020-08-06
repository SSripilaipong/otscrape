import re

from otscrape.base.projection import PathTokenizer, PathVisitor, DeniedDataStructure

pattern_attribute = r'[a-zA-Z_][a-zA-Z0-9_]*'


class AttributeTokenizer(PathTokenizer):
    def check(self, path: str):
        is_single_attr = re.match(r'^' + pattern_attribute + r'$', path)
        is_chained_attr = re.match(r'^' + pattern_attribute + r'\.', path)
        return is_single_attr or is_chained_attr

    def extract(self, path: str):
        name = re.findall(r'^(' + pattern_attribute + r')', path)
        path = '.'.join(path.split('.')[1:])

        return path, name

    def get_visitor(self, name):
        return AttributeVisitor(name)


class AttributeVisitor(PathVisitor):
    def __init__(self, name):
        super().__init__(name)

    def visit(self, data):
        try:
            v = data[self.name] if self.project else None
            ps = [data[self.name]]
        except ValueError:
            raise DeniedDataStructure()

        return self.next_visitors, ps, v
