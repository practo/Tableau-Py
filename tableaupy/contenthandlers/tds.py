# -*- coding: utf-8 -*-
"""This module defines tableau datasource content handler for
parsing tableau datasource files
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import lxml.etree as etree
import xmltodict

from tableaupy.contenthandlers import exceptions


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

        #: dict : tableau datasource metadata
        self._tds_metadata = dict()

        #: list[dict] : tableau datasource column information
        self._tds_columns = list()

    @property
    def column_definitions(self):
        """Column Definitions property

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
        """

        return [
            {key: column[key] for key in self._col_def_keys}
            for column in self._tds_columns
        ]

    @property
    def metadata(self):
        """Metadata property

        Returns
        -------
        dict
            datasource and connection attributes,
            represented as::

                {
                    'datasource': datasource attributes,
                    'connection': connection attributes
                }
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
        UnexpectedCount
            when more than 1 connection information is available
        UnexpectedEmptyInformation
            when datasource information is empty,
            when connection information is empty,
        """

        datasource = dict(tds_xml.attrib)

        if len(datasource) == 0:
            raise exceptions.UnexpectedEmptyInformation(
                self.K_METADATA_DATASOURCE
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
            raise exceptions.UnexpectedCount(
                identifier=self.K_METADATA_CONNECTION,
                expected=1,
                value=len(connections)
            )

        # dict because the lxml.etree.Element.attrib represents a dictionary
        # like class instance but not dictionary
        connection = dict(connections[0])

        if len(connection) == 0:
            raise exceptions.UnexpectedEmptyInformation(
                self.K_METADATA_CONNECTION
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
