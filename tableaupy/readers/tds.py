# -*- coding: utf-8 -*-
"""This module defines tableau datasource xml reader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tableaupy.contenthandlers.tds import TDSContentHandler
from tableaupy.readers.base import Reader


class TDSReader(Reader):
    """Reads Tableau datasource files (\\*.tds)

    Examples
    --------
    >>> from tableaupy.readers.tds import TDSReader
    >>> tds_reader = TDSReader()
    >>> tds_reader.read('sample/sample.tds')
    >>> tds_reader.extension
    '.tds'
    >>> tds_reader.get_datasource_metadata() == {
    ...     u'datasource': {
    ...         'formatted-name': 'Datasource Example',
    ...         'inline': 'true'
    ...     },
    ...     u'connection': {
    ...         'authentication': 'sqlserver',
    ...         'class': 'sqlserver',
    ...         'dbname': 'DATABASE_NAME',
    ...         'minimum-driver-version': 'SQL Server Native Client 10.0',
    ...         'odbc-native-protocol': 'yes',
    ...         'one-time-sql': '',
    ...         'server': '0.0.0.0',
    ...         'username': 'username'
    ...     }
    ... }
    True
    >>> tds_reader.get_datasource_column_defs()[:2] == [{
    ...     'parent-name': '[TABLE_NAME]',
    ...     'local-name': '[LOCAL_COLUMN_NAME1]',
    ...     'local-type': 'date',
    ... },
    ... {
    ...      'parent-name': '[TABLE_NAME]',
    ...      'local-name': '[LOCAL_COLUMN_NAME2]',
    ...      'local-type': 'string',
    ... }]
    True
    """

    def __init__(self):
        super(TDSReader, self).__init__('.tds', TDSContentHandler)

    def get_datasource_column_defs(self):
        """Gets tableau datasource column information

        Returns
        -------
        TDSContentHandler.column_definitions
            column information of datasource file read
        """

        return self._xml_content_handler.column_definitions

    def get_datasource_metadata(self):
        """Gets tableau datasource metadata information

        Returns
        -------
        TDSContentHandler.metadata
            metadata information of datasource file read
        """

        return self._xml_content_handler.metadata
