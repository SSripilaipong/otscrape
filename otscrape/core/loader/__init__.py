from .dummy import DummyLoader
from .request import SimpleRequestLoader
from .file import LineLoader, JSONFileLoader, CSVFileLoader

__all__ = ['DummyLoader', 'SimpleRequestLoader', 'LineLoader', 'JSONFileLoader', 'CSVFileLoader']
