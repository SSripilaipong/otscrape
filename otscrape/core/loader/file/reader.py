class LineReader:
    def __init__(self, skiprows=0):
        self.skiprows = skiprows

    def _do_skiprows(self):
        for _ in range(self.skiprows):
            _ = self.read_line()

    def _open(self):
        raise NotImplementedError()

    def open(self):
        self._open()

        self._do_skiprows()

    def close(self):
        raise NotImplementedError()

    def is_eof(self):
        raise NotImplementedError()

    def read_line(self):
        raise NotImplementedError()
