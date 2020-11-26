from otscrape.core.base.extractor import extractor, Attribute, Extractor
from otscrape.core.base.state import PickleState

from otscrape.core.extractor import (Raw, RequestText, RequestStatusCode, JSON, DictPath, XPath, ZipDict, RegEx, chain,
                                     TextSoup, SoupFindAll, SoupSelect, FileContent, FileName, FileLineNumber)

from otscrape.core.loader import SimpleRequestLoader, DummyLoader, LineLoader

from otscrape.core.base.page import PageBase
from otscrape.core.page import Page, DataPage, FileLinePage

from otscrape.core.exporter import JSONExporter

from otscrape.core.worker import Workers

from otscrape.core.pandas import scrape_pandas

import otscrape.core.magics
