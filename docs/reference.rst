Reference
==========

Page Classes and Functions
---------------------------------

.. autoclass:: otscrape.Page
   :special-members: __getitem__, __setitem__
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: otscrape.DataPage

.. autoclass:: otscrape.FileLinePage
   :members: iter_lines, apply, reset
   :undoc-members:

.. autoclass:: otscrape.JSONLinePage
   :members: iter_lines, apply, reset
   :undoc-members:

.. autoclass:: otscrape.CSVLinePage
   :members: iter_lines, apply, reset
   :undoc-members:


Extractor Classes and Functions
--------------------------------------

.. autoclass:: otscrape.Raw
   :members:


.. autoclass:: otscrape.RequestText
   :members:


.. autoclass:: otscrape.RequestStatusCode
   :members:


.. autoclass:: otscrape.JSON
   :members:


.. autoclass:: otscrape.DictPath
   :members:


.. autoclass:: otscrape.XPath
   :members:


.. autoclass:: otscrape.ZipDict
   :members:


.. autoclass:: otscrape.RegEx
   :members:


.. autoclass:: otscrape.Chain
   :members:


.. autoclass:: otscrape.ChainMap
   :members:


.. autoclass:: otscrape.Map
   :members:


.. autoclass:: otscrape.StarMap
   :members:


.. autoclass:: otscrape.Lambda
   :members:


.. autoclass:: otscrape.StarLambda
   :members:


.. autoclass:: otscrape.TextSoup
   :members:


.. autoclass:: otscrape.SoupFindAll
   :members:


.. autoclass:: otscrape.SoupSelect
   :members:


.. autoclass:: otscrape.FileContent
   :members:


.. autoclass:: otscrape.FileName
   :members:


.. autoclass:: otscrape.FileLineNumber
   :members:


.. autoclass:: otscrape.Extractor
   :members:


.. autoclass:: otscrape.Attribute
   :members:


.. autofunction:: otscrape.extractor


Exporter Classes and Functions
-------------------------------------

.. autoclass:: otscrape.JSONExporter
   :members:
   :undoc-members:


Loader Classes and Functions
-----------------------------------

.. autoclass:: otscrape.SimpleRequestLoader
   :members:
   :undoc-members:

.. autoclass:: otscrape.DummyLoader
   :members:
   :undoc-members:

.. autoclass:: otscrape.LineLoader
   :members:
   :undoc-members:

.. autoclass:: otscrape.JSONFileLoader
   :members:
   :undoc-members:

.. autoclass:: otscrape.CSVFileLoader
   :members:
   :undoc-members:


Worker Classes and Functions
------------------------------------

.. autoclass:: otscrape.Workers
   :members:
   :undoc-members:

.. autofunction:: otscrape.PickleState

.. autoclass:: otscrape.core.base.state.PickleStateBase
   :members:
   :inherited-members:
   :undoc-members:

