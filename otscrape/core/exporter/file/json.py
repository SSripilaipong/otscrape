import json

from .base import FileExporter


class JSONExporter(FileExporter):
    def __init__(self, filename, mode='w', encoding=None, lines=True, **kwargs):
        super().__init__(filename=filename, mode=mode, encoding=encoding, **kwargs)

        self.lines = lines

    def get_data_to_write(self, data):
        if self.lines:
            text = json.dumps(data, ensure_ascii=False, default=str)
        else:
            text = str(data)

        return text + '\n'
