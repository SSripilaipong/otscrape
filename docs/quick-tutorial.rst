Quick Tutorial
================

Get Started
------------

One can write scripts in file `.py` and execute using python command
or use interactive Python editors, eg. IPython, Jupyter Notebook, or Google Colab.

For Windows users, Google Colab is recommended to avoid operating system issues, or see this note: :ref:`Running otscrape on Windows`

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


Components Overview
--------------------

Page
`````

The main component that will be used when scraping and making any calculation with `otscrape` is a `Page`.

A `Page` is where a single scraping unit is defined which is how the data will be loaded in,
and what will be computed from the *raw* data.

So, a `Page` is composed of 2 types of components:

:- Loader: handles the raw data loading logic
:- `Extractor`_: handles the attribute computing logic

By default, a `Page` will use `SimpleRequestLoader` as its `Loader`
and parameters for the loader will be passed by attributes whose name starts with "_loader__".
Please see :ref:`Page types and Loaders` for more information on other possible loading methods.

**[Example] Simple Page:**

.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('//title/text()', only_first=True)
        status = ot.RequestStatusCode()


    print(MyPage('https://en.wikipedia.org/wiki/Python_(programming_language)').get_data())
    print(MyPage('https://en.wikipedia.org/wiki/Web_scraping').get_data())

.. testoutput::

    {'title': 'Python (programming language) - Wikipedia', 'status': 200}
    {'title': 'Web scraping - Wikipedia', 'status': 200}

Where `ot.XPath` and `RequestStatusCode` are the extractors,
extracting the result from `SimpleRequestLoader` which is implicitly defined by `ot.Page`.

When the `get_data()` method is called, `MyPage` will load the raw data using its Loader.
And all *projectable* attributes will be computed using the defined Extractors which, then, are aggregated into a dictionary.

**For better performance, loaders are designed not to load the raw data until it's needed,**
**eg. get_data() is called or a user tries to access an attribute which has to take raw data as an input.**

**As well as all the extractors, they will not be executed until it's needed.**

**Once an attribute is computed, it will be stored in the page,**
**and will be returned every time it's accessed instead of recomputing the value.**


**[Example] Passing parameters to Loader:**


.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        _loader__method = 'GET'  # default is 'GET'
        _loader__rate_limit = '1/3'
        _loader_max_retries = 5

        title  = ot.XPath('//title/text()', only_first=True)
        status = ot.RequestStatusCode()


    print(MyPage('https://en.wikipedia.org/wiki/Python_(programming_language)').get_data())
    print(MyPage('https://en.wikipedia.org/wiki/Web_scraping').get_data())

.. testoutput::

    {'title': 'Python (programming language) - Wikipedia', 'status': 200}
    {'title': 'Web scraping - Wikipedia', 'status': 200}

In the example above, parameters `method`, `max_retries`, and `rate_limit` will be passed to the `SimpleRequestLoader`
by assigning attributes `_loader__method`, `_loader_max_retries` and `_loader__rate_limit`.

**[Example] Make the Page more user-friendly:**

To avoid passing full URLs every time an instance is created, one might override the constructor to do the job as follow.

.. testcode::

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

.. testoutput::
    :hide:

    {'title': 'Python (programming language) - Wikipedia', 'status': 200}
    {'title': 'Web scraping - Wikipedia', 'status': 200}

Extractor
``````````

An `Extractor` are used for extracting information from raw data loaded in the `Page`.
Commonly used extraction logics are provided such as XPath(), SoupSelect(), JSON(), or RegEx(), see the full list :ref:`Extractor Classes and Functions`

One can also implement a custom Extractor class by inheriting from class `Extractor`. See this note for more information: :ref:`Implementing a custom Extractor`

When an extractor is defined within a page class, an attribute with the same name will represent the value from the extractor.

**[Example] Access an attribute value**

.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('//title/text()', only_first=True)


    p = MyPage('https://en.wikipedia.org/wiki/Web_scraping')

    print(p['title'])  # The loader will load raw data from the url here. Then XPath() extractor processes it.

.. testoutput::

    Web scraping - Wikipedia


An extractor can, also, take in a result from another extractor by specifying `target` parameter, which is, by default, set to `target='raw'`.


**[Example] An extractor processes result from another extractor**

.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('//title/text()', only_first=True)
        first_word = ot.RegEx(r'(\w+)', only_first=True, select=0, target=title)


    p = MyPage('https://en.wikipedia.org/wiki/Web_scraping')

    print(p['title'])
    print(p['first_word'])
    print(p.get_data())

.. testoutput::

    Web scraping - Wikipedia
    Web
    {'title': 'Web scraping - Wikipedia', 'first_word': 'Web'}


By default, when get_data() is called, all attributes are returned. Unless `project=False` is set at its extractor.
However, its value's still accessible.


**[Example] Non-projectable extractor**

.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('//title/text()', only_first=True, project=False)
        first_word = ot.RegEx(r'(\w+)', only_first=True, select=0, target=title)


    p = MyPage('https://en.wikipedia.org/wiki/Web_scraping')

    print(p.get_data())
    print(p['title'])  # still accessible

.. testoutput::

    {'first_word': 'Web'}
    Web scraping - Wikipedia


When an error occurred with an extractor while processing data, the result, by default, will be replaced with `None`,
and a warning message will be raised.
The replace value can be set using parameter `replace_error`.


**[Example] Replacing error in an extractor**

.. testcode::

    import otscrape as ot


    class MyPage(ot.Page):
        title  = ot.XPath('a wrong syntax', only_first=True,  # 'a wrong syntax' will cause an error
                          replace_error='TITLE ERROR')


    p = MyPage('https://en.wikipedia.org/wiki/Web_scraping')

    print(p.get_data())

.. testoutput::

    {'title': 'TITLE ERROR'}

