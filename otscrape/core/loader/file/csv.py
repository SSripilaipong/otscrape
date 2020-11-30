import csv

from .file import LineLoader, TextFileLineReader


def get_file_params(kwargs):
    file_params = {'mode': 'r'}
    file_params.update({k[5:]: v for k, v in kwargs.items() if not k.startswith('file__')})
    return file_params


def get_csv_params(kwargs):
    csv_params = {'delimiter': ',', 'quotechar': '"'}
    csv_params.update({k[5:]: v for k, v in kwargs.items() if k.startswith('csv__')})
    return csv_params


class CSVLineReader(TextFileLineReader):
    def __init__(self, filename, skiprows=0, **params):
        file_params = {k: v for k, v in params.items() if not k.startswith('csv__')}
        super().__init__(filename, skiprows=skiprows, **file_params)

        self.csv_params = get_csv_params(self.params)

        self.reader = None
        self._is_eof = False

    def _open(self):
        super()._open()

        self.reader = csv.DictReader(self.file, **self.csv_params)

    def read_line(self):
        try:
            return self.reader.__next__()
        except StopIteration as e:
            self._is_eof = True
            raise e

    def is_eof(self):
        return self._is_eof


class CSVFileLoader(LineLoader):
    def get_line_reader(self, filename):
        return CSVLineReader(filename, skiprows=self.skiprows, **self.kwargs)

    def calculate_tot_line(self):
        file_params = get_file_params(self.kwargs)
        csv_params = get_csv_params(self.kwargs)

        tot = sum(1 for filename in self.filenames for _ in csv.DictReader(open(filename, **file_params), **csv_params))

        return tot

    def do_load(self):
        line_obj = super().do_load()

        return line_obj.content
