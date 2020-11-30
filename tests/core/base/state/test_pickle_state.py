import pytest

import random
from tempfile import NamedTemporaryFile

import otscrape as ot


class ContentPage(ot.DataPage):
    key = ot.Attribute()
    data = ot.Raw()
    add_one = ot.Lambda(lambda t: t + 1)

    def __init__(self, i):
        super().__init__(i)
        self['key'] = i


class ListingPage(ot.DataPage):
    key = ot.Attribute()
    page = ot.DictPath('/page')
    children = ot.Chain([ot.DictPath('/children'), ot.Map(ContentPage)])

    def __init__(self, i):
        super().__init__({'page': i, 'children': list(range(i, i+5))})
        self['key'] = i


class FakeException(Exception):
    pass


def run_1loop(filename, stop_at, replace=False, assert_sequence=None):
    assert_sequence = assert_sequence or []
    enter_loop = False

    with ot.PickleState(filename, replace=replace) as s:
        for i, (ss, n) in enumerate(s.iter(range(1, 21))):
            enter_loop = True
            page = ListingPage(n)
            _ = page.get_data()
            if n == stop_at:
                raise FakeException()

            assert assert_sequence[i] == n

        if not enter_loop:
            assert len(assert_sequence) == 0


@pytest.mark.integration
@pytest.mark.ot_mp
@pytest.mark.ot_state
def test_1loop():
    with NamedTemporaryFile('w') as file:
        try:
            seq = [1, 2, 3, 4, 5, 6]
            run_1loop(file.name, stop_at=7, replace=True, assert_sequence=seq)
        except FakeException:
            pass

        try:
            seq = [7, 8, 9, 10, 11, 12, 13, 14]
            run_1loop(file.name, stop_at=15, replace=False, assert_sequence=seq)
        except FakeException:
            pass

        try:
            seq = [15, 16, 17, 18, 19, 20]
            run_1loop(file.name, stop_at=None, replace=False, assert_sequence=seq)
        except FakeException:
            pass

        try:
            seq = []
            run_1loop(file.name, stop_at=None, replace=False, assert_sequence=seq)
        except FakeException:
            pass


def run_2loop(filename, stop_at1=None, stop_at2=None, replace=False, assert_sequence1=None, assert_sequence2=None):
    assert_sequence1 = assert_sequence1 or []
    assert_sequence2 = assert_sequence2 or []

    enter_loop1, enter_loop2 = False, False

    with ot.Workers(3, state=filename, restart=replace) as w:
        ll = w.list()

        for i, n in enumerate(w.iter(range(1, 21))):
            enter_loop1 = True
            page = ListingPage(n)
            if page['page'] % 2 == 0:
                ll.append(page)

            if n == stop_at1:
                raise FakeException()

            assert assert_sequence1[i] == n

        if not enter_loop1:
            assert len(assert_sequence1) == 0

        for i, x in enumerate(ll):
            enter_loop2 = True
            _ = x.get_data()

            if x['page'] == stop_at2:
                raise FakeException()

            assert assert_sequence2[i] == x['page']

        if not enter_loop2:
            assert len(assert_sequence2) == 0


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.ot_mp
@pytest.mark.ot_state
def test_2loop_with_list():
    with NamedTemporaryFile('w', suffix='.pickle') as file:
        try:
            seq1 = [1, 2, 3, 4, 5, 6]
            seq2 = []
            run_2loop(file.name, stop_at1=7, replace=True,
                      assert_sequence1=seq1, assert_sequence2=seq2)
        except FakeException:
            pass

        try:
            seq1 = [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            seq2 = []
            run_2loop(file.name, stop_at1=15, replace=False,
                      assert_sequence1=seq1, assert_sequence2=seq2)
        except FakeException:
            pass

        try:
            seq1 = [2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 18, 19, 20]
            seq2 = [2, 4]
            run_2loop(file.name, stop_at1=None, stop_at2=6, replace=False,
                      assert_sequence1=seq1, assert_sequence2=seq2)
        except FakeException:
            pass

        try:
            seq1 = [6, 8, 10, 12, 14, 16, 18, 20]
            seq2 = [6, 8, 10, 12, 14]
            run_2loop(file.name, stop_at1=None, stop_at2=16, replace=False,
                      assert_sequence1=seq1, assert_sequence2=seq2)
        except FakeException:
            pass

        try:
            seq1 = [16, 18, 20]
            seq2 = [16, 18, 20]
            run_2loop(file.name, replace=False,
                      assert_sequence1=seq1, assert_sequence2=seq2)
        except FakeException:
            pass


def run_export(filename, export_filename, stop_at, assert_unique, size=10, replace=False):
    with ot.Workers(3, state=filename, restart=replace) as w:
        buffer = w.scrape(ListingPage(i) for i in range(1, size+1))

        for i, x in enumerate(buffer):
            w.export(x['children'], export_filename)

            if x['page'] == stop_at:
                raise FakeException()

            assert x['page'] in assert_unique
            assert_unique.remove(x['page'])


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.ot_mp
@pytest.mark.ot_state
@pytest.mark.ot_exporter
def test_export():
    for _ in range(3):
        with NamedTemporaryFile('wb', suffix='.pickle') as state_file, \
                NamedTemporaryFile('w', suffix='.json') as export_file:
            size = 10
            unique = set(range(1, size+1))

            try:
                run_export(state_file.name, export_file.name,
                           stop_at=5, replace=True,
                           assert_unique=unique)
            except FakeException:
                pass

            while unique:
                stop_at = random.choice(list(unique)) if len(unique) > 1 else None

                try:
                    run_export(state_file.name, export_file.name,
                               stop_at=stop_at, replace=False,
                               assert_unique=unique)
                except FakeException:
                    pass
