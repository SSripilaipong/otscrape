from collections.abc import Iterable
from requests import Response
import re

from otscrape.core.base.extractor import Extractor
from otscrape.core.extractor.request import RequestText


flag_table = (
    (('A', 'ASCII'), re.A),
    (('DEBUG',), re.DEBUG),
    (('L', 'LOCALE'), re.L),
    (('M', 'MULTILINE'), re.M),
    (('S', 'DOTALL'), re.S),
    (('X', 'VERBOSE'), re.X),
)


def get_flags(flags):
    if isinstance(flags, (re.RegexFlag, int)):
        flags = flags
    elif isinstance(flags, str):
        if not flags:
            flags = 0
        else:
            r = 0
            for f in flags.upper().split('|'):
                for key, value in flag_table:
                    if f in key:
                        r |= value
                        break
                else:
                    raise ValueError(f'Flag "{f}" is not recognized.')

            flags = r

    return flags


class RegEx(Extractor):
    def __init__(self, pattern, flags='', only_first=False, select=None, target=None, *,
                 project=True, replace_error=None, **kwargs):
        super().__init__(target=target, project=project, replace_error=replace_error)

        self.flags = get_flags(flags)
        self.only_first = only_first
        self.select = select
        self.pattern = re.compile(pattern, self.flags)
        self.kwargs = kwargs

    def extract(self, page, cache):
        target = self.target

        value = page[target]
        if isinstance(value, Response):
            value = RequestText(target=target).extract(page, None)

        assert isinstance(value, str)
        return self._extract_str(value)

    def _extract_str(self, value):
        it = self.pattern.finditer(value, **self.kwargs)

        result = []
        for match in it:
            group = match.groupdict()
            group.update({i: v for i, v in enumerate(match.groups())})

            if self.select is not None:
                if not isinstance(self.select, Iterable) or isinstance(self.select, str):
                    group = group[self.select]
                else:
                    group = {s: group.get(s, None) for s in self.select}

            result.append(group)

            if self.only_first:
                result = result[0]
                break

        return result
