# -*- coding: utf-8 -*-
"""
This module defines xml content handlers for parsing tableau files into
python objects

"""

from __future__ import absolute_import, unicode_literals

from auto_extract.xml_as_dictionary import XmlDictConfig


class TDSContentHandler(object):
    """
    Represents an object containing parsed information from a tableau datasource file

    """

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


        Examples
        --------
        >>> import lxml.etree as etree
        >>> datasource = etree.parse('sample/sample.tds').getroot()
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_content_handler.parse(datasource)
        >>> tds_content_handler.columns[:2] == [{
        ...     'ordinal': '1',
        ...     'parent-name': '[TABLE_NAME]',
        ...     'remote-type': '7',
        ...     'aggregation': 'Year',
        ...     'remote-alias': 'REMOTE_ALIAS1',
        ...     'remote-name': 'REMOTE_COLUMN_NAME1',
        ...      'attributes': {
        ...          'attribute': [{
        ...             'datatype': 'string',
        ...             'name': 'DebugRemoteType',
        ...             '_text': '"SQL_TYPE_DATE"'
        ...           },
        ...           {
        ...             'datatype': 'string',
        ...             'name': 'DebugWireType',
        ...             '_text': '"SQL_C_TYPE_DATE"'
        ...           },
        ...           {
        ...             'datatype': 'boolean',
        ...             'name': 'TypeIsDateTime2orDate',
        ...             '_text': 'true'
        ...           }]
        ...      },
        ...     'local-name': '[LOCAL_COLUMN_NAME1]',
        ...     'local-type': 'date',
        ...     'class': 'column',
        ...     'contains-null': 'true'
        ... },
        ... {
        ...      'ordinal': '2',
        ...      'parent-name': '[TABLE_NAME]',
        ...      'remote-type': '130',
        ...      'padded-semantics': 'true',
        ...      'aggregation': 'Count',
        ...      'remote-alias': 'REMOTE_ALIAS2',
        ...      'width': '100',
        ...      'remote-name': 'REMOTE_COLUMN_NAME2',
        ...      'attributes': {
        ...          'attribute': [{
        ...             'datatype': 'string',
        ...             'name': 'DebugRemoteType',
        ...             '_text': '"SQL_WVARCHAR"',
        ...           },
        ...           {
        ...             'datatype': 'string',
        ...             'name': 'DebugWireType',
        ...             '_text': '"SQL_C_WCHAR"',
        ...           },
        ...           {
        ...             'datatype': 'string',
        ...             'name': 'TypeIsVarchar',
        ...             '_text': '"true"',
        ...           }]
        ...      },
        ...      'collation': {
        ...          'flag': '2147483649',
        ...          'name': 'LEN_RUS_S2_VWIN'
        ...      },
        ...      'local-name': '[LOCAL_COLUMN_NAME2]',
        ...      'local-type': 'string',
        ...      'class': 'column',
        ...      'contains-null': 'true'
        ... }]
        True

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
        >>> import lxml.etree as etree
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
        self._tds_metadata['datasource'] = tds_xml.attrib

        connection = tds_xml.find('connection')
        connection_object = XmlDictConfig(connection)

        named_connections = connection_object.get('named-connections')

        assert named_connections is not None, 'named-connections does not exists'

        named_connection = named_connections.get('named-connection')

        assert named_connection is not None, 'named-connection does not exist'
        assert isinstance(named_connection, dict), 'named-connection is not an instance of dict'

        self._tds_metadata['connection'] = named_connection.get('connection')

        assert self._tds_metadata['connection'] is not None, 'connection information is none'
        assert isinstance(self._tds_metadata['connection'], dict), \
            'connection information is not dict'
        assert len(self._tds_metadata['connection']) != 0, 'connection information is empty'

        metadata_records = connection_object.get('metadata-records')

        if metadata_records is None:
            self._tds_columns = list()
            return

        assert isinstance(metadata_records, dict), 'metadata-records is not dict'

        self._tds_columns = metadata_records.get('metadata-record')

        assert self._tds_columns is not None, 'no tag metadata-record exists'

        # when only one column information is returned it will be in form of dict
        # thus we need to convert it into list
        if isinstance(self._tds_columns, dict):
            self._tds_columns = [self._tds_columns]

        assert isinstance(self._tds_columns, list), 'tds_columns not a list'


if __name__ == '__main__':
    import doctest

    doctest.testmod()