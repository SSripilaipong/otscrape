from otscrape.core.base.exporter import Exporter


class FileExporter(Exporter):
    def __init__(self, filename, mode='w', encoding=None, **kwargs):
        super().__init__(**kwargs)

        self.filename = filename
        self.mode = mode
        self.encoding = encoding

        self.file = None

    def on_open(self):
        self.file = open(self.filename, self.mode, encoding=self.encoding)

    def get_data_to_write(self, data):
        raise NotImplementedError()

    def export(self, data):
        self.file.write(self.get_data_to_write(data))
        # self.file.flush()

    def on_close(self):
        self.file.close()
