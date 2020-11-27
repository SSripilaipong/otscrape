import csv

from .file import LineLoader


def csv_split(content):
    return list(csv.reader([content], delimiter=',', quotechar='"'))[0]


class CSVFileLoader(LineLoader):
    def __init__(self, filenames=None, rate_limit='', fetch_size=None, parallel=False, **kwargs):
        super().__init__(filenames=filenames, rate_limit=rate_limit, fetch_size=fetch_size, skiprows=1,
                         parallel=parallel, **kwargs)

        if hasattr(self, 'filenames'):
            self.headers = {filename: csv_split(next(open(filename, 'r'))) for filename in self.filenames}
        else:
            self.headers = []

    def do_load(self):
        line_obj = super().do_load()

        values = csv_split(line_obj.content)
        data = dict(zip(self.headers[line_obj.filename], values))

        return data
