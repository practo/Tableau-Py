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
