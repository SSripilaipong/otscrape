Quick Tutorial
================

Get Started
------------

One can write scripts in file `.py` and execute using python command
or use interactive Python editors, eg. IPython, Jupyter Notebook, or Google Colab.

For Windows users, Google Colab is recommended to avoid operating system issues, or see this note: `Running otscrape on Windows <#>`_

Installation
--------------

Requirements
``````````````

.. hlist::
    :columns: 1

    * Python 3.6+
    * Works on Linux, Windows, macOS, BSD


Using Pip
```````````

.. code-block:: shell

    $ pip install one-two-scrape


Components
-----------

Page
`````

The main component that will be used when scraping and making any calculation with `otscrape` is a `Page`.

A `Page` is where a single scraping unit is defined which is how the data will be loaded in,
and what will be computed from the *raw* data.

So, a `Page` is composed of 2 types of components:

:- Loader: handles the raw data loading logic
:- Extractor: handles the attribute computing logic

By default, a `Page` will use `SimpleRequestLoader` as its `Loader`
and parameters for the loader will be passed by attributes whose name starts with "_loader__".
Please see `Page types and Loaders <#>`_ for more information on other possible loading methods.

**[Example] Simple Page:**

.. code-block:: python

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('//title/text()', only_first=True)
        status = ot.RequestStatusCode()


    print(MyPage('https://en.wikipedia.org/wiki/Python_(programming_language)').get_data())
    print(MyPage('https://en.wikipedia.org/wiki/Web_scraping').get_data())

.. code-block::

    {'title': 'Python (programming language) - Wikipedia', 'status': 200}
    {'title': 'Web scraping - Wikipedia', 'status': 200}

Where `ot.XPath` and `RequestStatusCode` are the extractors,
extracting the result from `SimpleRequestLoader` which is implicitly defined by `ot.Page`.

When the `get_data` method is called, `MyPage` will load the raw data using its Loader.
And all *projectable* attributes will be computed using the defined Extractors.

**[Example] Passing parameters to Loader:**

.. code-block:: python

    import otscrape as ot


    class MyPage(ot.Page):
        _loader__method = 'GET'  # default is 'GET'
        _loader__rate_limit = '1/3'
        _loader_max_retries = 5

        title  = ot.XPath('//title/text()', only_first=True)
        status = ot.RequestStatusCode()


    print(MyPage('https://en.wikipedia.org/wiki/Python_(programming_language)').get_data())
    print(MyPage('https://en.wikipedia.org/wiki/Web_scraping').get_data())


.. code-block::

    {'title': 'Python (programming language) - Wikipedia', 'status': 200}
    {'title': 'Web scraping - Wikipedia', 'status': 200}

In the example above, parameters `method`, `max_retries`, and `rate_limit` will be passed to the `SimpleRequestLoader`
by assigning attributes `_loader__method`, `_loader_max_retries` and `_loader__rate_limit`.

**[Example] Make the Page more user-friendly:**

To avoid passing full URLs every time an instance is created, one might override the constructor to do the job as follow.

.. code-block:: python

    import otscrape as ot


    class MyPage(ot.Page):
        _loader__method = 'GET'
        _loader__rate_limit = '1/3'
        _loader_max_retries = 5

        title  = ot.XPath('//title/text()', only_first=True)
        status = ot.RequestStatusCode()

        def __init__(self, keyword):
            super().__init__('https://en.wikipedia.org/wiki/' + keyword)


    print(MyPage('Python_(programming_language)').get_data())
    print(MyPage('Web_scraping').get_data())
