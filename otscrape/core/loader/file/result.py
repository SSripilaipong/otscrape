class FileResult:
    def __init__(self, filename, content):
        self.content = content
        self.filename = filename

    def __repr__(self):
        n_char = 20
        content = self.content if len(self.content) < n_char else f'{self.content[:n_char]}...'
        return f'FileResult({self.filename!r}, {content!r})'


class LineObject(FileResult):
    def __init__(self, filename, line_no, content):
        super().__init__(filename, content)

        self.line_no = line_no

    def __repr__(self):
        n_char = 20
        content = self.content if len(self.content) < n_char else f'{self.content[:n_char]}...'
        return f'LineObject({self.filename!r}, {self.line_no}, {content!r})'
