# -*- coding: utf-8 -*-
"""
This module defines xml content handlers for parsing tableau files into
python objects
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import lxml.etree as etree
import xmltodict

from auto_extract import error_messages as err_msgs


class TDSParseException(Exception):
    """Exception for tds parsing related issues"""

    def __init__(self, *args, **kwargs):
        super(TDSParseException, self).__init__(*args, **kwargs)


class TDSContentHandler(object):
    """Instance of parsed tableau datasource file"""

    K_COL_DEF_PARENT_NAME = 'parent-name'
    K_COL_DEF_LOCAL_NAME = 'local-name'
    K_COL_DEF_LOCAL_TYPE = 'local-type'

    K_METADATA_DATASOURCE = 'datasource'
    K_METADATA_CONNECTION = 'connection'

    _col_def_keys = [
        K_COL_DEF_PARENT_NAME,
        K_COL_DEF_LOCAL_NAME,
        K_COL_DEF_LOCAL_TYPE,
    ]

    def __init__(self):
        super(TDSContentHandler, self).__init__()

        #: dict: tableau datasource metadata
        self._tds_metadata = dict()

        #: list[dict]: tableau datasource column information
        self._tds_columns = list()

    @property
    def column_definitions(self):
        """Column Definitions property

        Column Definitions parsed from tableau datasource file

        Returns
        -------
        list
            list of dictionary items containing column information
            represented as::

                {
                    'local-name': local name of column,
                    'parent-name': name of the table containing column
                    'local-type': local data type of column,
                }

        Examples
        --------
        >>> import lxml.etree as etree
        >>> datasource = etree.parse('sample/sample.tds').getroot()
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_content_handler.parse(datasource)
        >>> tds_content_handler.column_definitions[:2] == [{
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

        return [
            {key: column[key] for key in self._col_def_keys}
            for column in self._tds_columns
        ]

    @property
    def metadata(self):
        """Metadata property

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
        >>> import lxml.etree as etree
        >>> datasource = etree.parse('sample/sample.tds').getroot()
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_content_handler.parse(datasource)
        >>> tds_content_handler.metadata == {
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
        """

        return self._tds_metadata

    def parse(self, tds_xml):
        """Parses tableau datasource xml tree

        Parameters
        ----------
        tds_xml : :py:obj:`~lxml.etree.Element`
            element tree representing a tableau datasource

        Raises
        ------
        TDSParseException
            when datasource infromation is empty,
            when connection information is empty,
            when more than 1 connection information is available
        """

        datasource = dict(tds_xml.attrib)

        if len(datasource) == 0:
            raise TDSParseException(
                err_msgs.EMPTY_INFORMATION.format(self.K_METADATA_DATASOURCE)
            )

        connection_path = '/'.join([
            'connection',
            'named-connections',
            'named-connection',
            'connection'
        ])
        connections = list()

        for connection in tds_xml.iterfind(connection_path):
            connections.append(connection.attrib)

        if len(connections) != 1:
            raise TDSParseException(
                err_msgs.UNEXPECTED_COUNT.format(
                    self.K_METADATA_CONNECTION, 1, len(connections)
                )
            )

        # dict because the lxml.etree.Element.attrib represents a dictionary
        # like class instance but not dictionary
        connection = dict(connections[0])

        if len(connection) == 0:
            raise TDSParseException(
                err_msgs.EMPTY_INFORMATION.format(self.K_METADATA_CONNECTION)
            )

        metadata_record_path = '/'.join([
            'connection',
            'metadata-records',
            'metadata-record'
        ])
        columns = list()

        for metadata_record in tds_xml.iterfind(metadata_record_path):
            xml_dict = xmltodict.parse(etree.tostring(metadata_record))
            columns.append(xml_dict.get('metadata-record'))

        self._tds_metadata = {
            self.K_METADATA_DATASOURCE: datasource,
            self.K_METADATA_CONNECTION: connection,
        }

        self._tds_columns = columns
