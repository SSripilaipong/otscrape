import pytest
import json
from tempfile import NamedTemporaryFile

import otscrape as ot


class ContentPage(ot.DataPage):
    data = ot.Raw()
    add_one = ot.Lambda(lambda t: t + 1)


class ListingPage(ot.DataPage):
    page = ot.DictPath('/page')
    children = ot.Chain([ot.DictPath('/children'), ot.Map(ContentPage)])


def test_exporter():
    with NamedTemporaryFile('w', suffix='.json') as f:
        with ot.JSONExporter(f.name) as export:
            for x in (ListingPage({'page': i, 'children': list(range(i, i+5))}) for i in range(5)):
                for y in x.get_data()['children']:
                    export(y)

        result = [json.loads(line)['add_one'] for line in open(f.name, 'r')]

    assert len(result) == 5*5

    for i in range(1, 10):
        assert sum(1 for x in result if x == i) == -abs(5-i) + 5


@pytest.mark.integration
def test_exporter_with_workers():
    with NamedTemporaryFile('w', suffix='.json') as f:
        with ot.JSONExporter(f.name, parallel=True) as exporter, ot.Workers(3) as w:
            buffer = w.scrape(ListingPage({'page': i, 'children': list(range(i, i+5))}) for i in range(5))

            for i, x in enumerate(buffer):
                for y in x['children']:
                    w.export(y, exporter)

        result = [json.loads(line)['add_one'] for line in open(f.name, 'r')]

    assert len(result) == 5*5

    for i in range(1, 10):
        assert sum(1 for x in result if x == i) == -abs(5-i) + 5


@pytest.mark.integration
def test_exporter_shorthand_with_workers():
    with NamedTemporaryFile('w', suffix='.json') as f:
        with ot.Workers(3) as w:
            buffer = w.scrape(ListingPage({'page': i, 'children': list(range(i, i+5))}) for i in range(5))

            for i, x in enumerate(buffer):
                for y in x['children']:
                    w.export(y, f.name)

        result = [json.loads(line)['add_one'] for line in open(f.name, 'r')]

    assert len(result) == 5*5

    for i in range(1, 10):
        assert sum(1 for x in result if x == i) == -abs(5-i) + 5
