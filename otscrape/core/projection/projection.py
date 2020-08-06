from typing import Dict, List, Union

from otscrape.base import Page
from otscrape.base.projection import PathVisitor, DeniedDataStructure
from .tokenizers import AttributeTokenizer


PathType = Dict[str, Union[str, 'PathType']]

projection_tokenizers = [
    AttributeTokenizer(),
]


class DeniedProjectionPath(Exception):
    pass


def get_visitors_from_string(path: str):
    visitors = []  # type: List[PathVisitor]

    while path:
        for tokenizer in projection_tokenizers:
            path, (name, visitor) = tokenizer.tokenize(path)
            if name is not None:
                if visitors:
                    visitors[-1].next_visitors.append(visitor)
                visitors.append(visitor)
                break
        else:
            raise DeniedProjectionPath()

    return visitors


def get_visitors(path: PathType):
    stack = []
    fields = []

    def _add_to_stack(visitors_so_far, path_dict: PathType):
        for key, value in path_dict.items():
            visitors = get_visitors_from_string(key)
            if visitors_so_far:
                visitors_so_far[-1].next_visitors.append(visitors[0])

            if isinstance(value, str):
                visitors[-1].project = value
                fields.append(value)
            elif isinstance(value, dict):
                stack.append((visitors_so_far + visitors, value))
            else:
                raise DeniedProjectionPath()

    _add_to_stack([], path)
    result = [v[0] for v, p in stack]

    while stack:
        vs, p = stack.pop()
        _add_to_stack(vs, p)

    return result, fields


class Projection:
    def __init__(self, path: PathType):
        self.path = path
        self.visitors, self.fields = get_visitors(self.path)  # type: List[PathVisitor], str
        self.dropped_fields = set()

        self.data = {}

    def visit(self, page: Page):
        interested_pages = []
        next_visitors = []

        data_updated = False
        for visitor in self.visitors:
            try:
                vs, next_pages, data = visitor.visit(page)
            except DeniedDataStructure():
                self.dropped_fields.update(visitor.fields)
                continue

            if visitor.project:
                self.data[visitor.project] = data
                data_updated = True

            next_pages = [p for p in next_pages if isinstance(p, Page)]
            if not next_pages:
                self.dropped_fields.update(visitor.fields)
                continue

            interested_pages.extend(next_pages)

        data_completed = set(self.fields) - self.dropped_fields == set(self.data.keys())
        data = self.data if data_updated and data_completed else None

        self.visitors = next_visitors

        return interested_pages, data
