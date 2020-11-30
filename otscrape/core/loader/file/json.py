import json

from .file import LineLoader


class JSONFileLoader(LineLoader):
    def do_load(self):
        line_obj = super().do_load()
        json_data = json.loads(line_obj.content)

        return json_data
