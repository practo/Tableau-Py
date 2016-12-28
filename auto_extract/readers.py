# -*- coding: utf-8 -*-
"""
This module defines xml readers for tableau files

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import lxml.etree as etree
from pathlib2 import Path
from tableausdk.Extract import TableDefinition
from tableausdk.Types import Collation
from tableausdk.Types import Type

from auto_extract import constants
from auto_extract import error_messages as err_msgs


class TDSReader(object):
    """
    Represents a reader object that reads tableau datasource file (\\*.tds)


    Parameters
    ----------
    xml_content_handler : TDSContentHandler
        content handler to parse information from tableau datasource xml information into

    """

    _parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    _type_map = {
        'boolean': Type.BOOLEAN,
        'string': Type.CHAR_STRING,
        'date': Type.DATE,
        'datetime': Type.DATETIME,
        'integer': Type.INTEGER,
        'double': Type.DOUBLE,
        'duration': Type.DURATION,
        'unicode_string': Type.UNICODE_STRING,
    }

    def __init__(self, xml_content_handler):
        super(TDSReader, self).__init__()
        self._xml_content_handler = xml_content_handler

    def define_table(self, collation=Collation.EN_US_CI):
        """
        Creates a TableDefinition object from the column information returned after parsing
        the tableau datasource file

        Other Parameters
        ----------------
        collation : :py:attr:`~tableausdk.Types.Collation`

        Returns
        -------
        :tableausdk:`TableDefinition <classtableausdk_1_1_extract_1_1_table_definition>`

        Raises
        ------
        :tableausdk:`TableauException <classtableausdk_1_1_exceptions_1_1_tableau_exception>`

        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')
        >>> tds_reader.define_table().getColumnCount()
        9

        """
        table_definition = TableDefinition()
        column_definitions = self.get_datasource_column_defs()

        table_definition.setDefaultCollation(collation)

        for i, definition in enumerate(column_definitions, start=1):
            parent_name = definition.get(constants.COL_DEF_PARENT_NAME)
            local_name = definition.get(constants.COL_DEF_LOCAL_NAME)
            local_type = definition.get(constants.COL_DEF_LOCAL_TYPE)

            assert_msg = err_msgs.IS_NONE + 'at: {}: {!s}\n'

            assert parent_name is not None, \
                assert_msg.format(constants.COL_DEF_PARENT_NAME, i, definition)

            assert local_name is not None, \
                assert_msg.format(constants.COL_DEF_LOCAL_NAME, i, definition)

            assert local_type is not None, \
                assert_msg.format(constants.COL_DEF_LOCAL_TYPE, i, definition)

            column_name = '{}.{}'.format(parent_name, local_name)
            column_type = self._type_map.get(local_type, self._type_map['unicode_string'])

            table_definition.addColumn(column_name, column_type)

        return table_definition

    def get_datasource_column_defs(self):
        """
        Returns read tableau datasource column information

        Returns
        -------
        TDSContentHandler.column_definitions

        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')

        """
        tds_content = self._xml_content_handler

        return tds_content.column_definitions

    def get_datasource_metadata(self):
        """
        Returns read tableau datasource metadata information

        Returns
        -------
        TDSContentHandler.metadata

        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')

        """
        tds_content = self._xml_content_handler

        return tds_content.metadata

    def read(self, tds_file):
        """
        Reads tableau datasource file into `xml_content_handler`

        Parameters
        ----------
        tds_file : str
            path to tableau datasource file


        Raises
        ------
        :py:exc:`~exceptions.OSError`
            when `tds_file` is not readable
        :py:exc:`~lxml.etree.XMLSchemaParseError`
            when `tds_file` is not xml parsable


        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')

        """
        tds_file_path = Path(tds_file)

        if not tds_file_path.exists():
            raise IOError(err_msgs.FILE_NO_EXISTS.format(tds_file))

        absolute_path = str(tds_file_path.resolve())

        if not tds_file_path.is_file():
            raise IOError(err_msgs.NOT_FILE.format(tds_file))

        if not os.access(absolute_path, os.R_OK):
            raise IOError(err_msgs.NOT_READABLE.format(tds_file))

        if tds_file_path.suffix != constants.TDS_EXTENSION:
            raise IOError(err_msgs.FILE_NOT_TDS.format(tds_file))

        tree = etree.parse(absolute_path, parser=self._parser)
        root = tree.getroot()

        self._xml_content_handler.parse(root)
