.. AutoExtract documentation master file, created by
   sphinx-quickstart on Mon Dec 19 20:04:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AutoExtract's documentation!
=======================================

Usage
-----
Calling for help

::

    $ auto_extract --help

To Create tableau datasource extracts from datasource files

::

    $ auto_extract file1.tds file2.tds

or with overwrite option

::

    $ auto_extract --overwrite *.tds

Add static suffix or prefix to generated files

::

    $ auto_extract --prefix TDE_ --suffix _SUFFIX *.tds


Contents:

.. toctree::
   :maxdepth: 2

   modules
   external_dependencies


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
