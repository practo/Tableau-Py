# -*- coding: utf-8 -*-
"""
This module defines xml content handlers for parsing tableau files into
python obects

Content Handlers
----------------
    - `TDSContentHandler`

"""

from __future__ import absolute_import, unicode_literals

import lxml.etree as etree


class TDSContentHandler(object):
    """
    Represents an object containing parsed information from a tableau datasource file

    """

    #: :py:obj:`~lxml.etree.XPath`: to find datasource element from element tree
    _datasource = etree.XPath('../datasource')

    #: :py:obj:`~lxml.etree.XPath`: to find connection element from element tree
    _connection = etree.XPath('connection')

    #: :py:obj:`~lxml.etree.XPath`: to find named connection elements from connection element tree
    _named_connection = etree.XPath('named-connections/named-connection')

    #: :py:obj:`~lxml.etree.XPath`: to find relation elements from connection element tree
    _relation = etree.XPath('relation')

    #: :py:obj:`~lxml.etree.XPath`: to find metadata record elements from connection element tree
    _metadata_record = etree.XPath('metadata-records/metadata-record[@class="column"]')

    def __init__(self):
        super(TDSContentHandler, self).__init__()

        #: dict: tableau datasource metadata
        self._tds_metadata = dict()

        #: list[dict]: tableau datasource column information
        self._tds_columns = list()

    @property
    def columns(self):
        """
        Information of columns within parsed tableau datasource

        Returns
        -------
        list
            list of dictionary items containing column information
            represented as::

                {
                    'local-name': local name of column,
                    'parent-name': name of the table containing column
                    'remote-name': name of column in `parent-name`,
                    'local-type': local data type of column,
                    'aggregation': column aggregated on,
                    'contains-null': if column contains null values
                    ...
                }

        """
        return self._tds_columns

    @property
    def metadata(self):
        """
        Metadata information of parsed tableau datasource

        Returns
        -------
        dict
            datasource and connection attributes,
            represented as::

                {
                    'datasource': datasource attributes,
                    'connection': connection attributes
                }


        Examples
        --------
        >>> datasource = etree.parse('sample/sample.tds').getroot()
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_content_handler.parse(datasource)
        >>> tds_content_handler.metadata == {
        ...     u'datasource': {
        ...             'formatted-name': 'Datasource Example',
        ...             'inline': 'true'
        ...     },
        ...     u'connection': {
        ...             'authentication': 'sqlserver',
        ...             'class': 'sqlserver',
        ...             'dbname': 'DATABASE_NAME',
        ...             'minimum-driver-version': 'SQL Server Native Client 10.0',
        ...             'odbc-native-protocol': 'yes',
        ...             'one-time-sql': '',
        ...             'server': '0.0.0.0',
        ...             'username': 'username'
        ...     }
        ... }
        True

        """
        return self._tds_metadata

    def parse(self, tds_xml):
        """
        Parses tableau datasource xml to fill metadata and column information

        Parameters
        ----------
        tds_xml : :py:obj:`~lxml.etree.Element`
            element tree representing a tableau datasource

        """
        self._tds_metadata['datasource'] = self._datasource(tds_xml)[0].attrib

        connection = self._connection(tds_xml)[0]
        named_connection = self._named_connection(connection)[0]

        self._tds_metadata['connection'] = self._connection(named_connection)[0].attrib
