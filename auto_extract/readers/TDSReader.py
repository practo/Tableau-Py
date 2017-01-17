# -*- coding: utf-8 -*-
"""This module defines tableau datasource xml reader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

import lxml.etree as etree
from pathlib2 import Path
from six import reraise
from tableausdk.Extract import TableDefinition
from tableausdk.Types import Collation
from tableausdk.Types import Type

from auto_extract import _constants
from auto_extract import _error_messages as err_msgs
from auto_extract.content_handlers import ContentHandlerException
from auto_extract.content_handlers import TDSContentHandler
from auto_extract.readers.exceptions import ReaderException
from auto_extract.readers.Reader import Reader


class TDSReader(Reader):
    """Reader class for Tableau datasource files (\\*.tds)

    Parameters
    ----------
    xml_content_handler : TDSContentHandler
        content handler to parse information from tableau datasource
        parsed information will be saved in this object
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
        super(TDSReader, self).__init__(_constants.TDS_EXTENSION)
        self._xml_content_handler = xml_content_handler

    def define_table(self, collation=Collation.EN_US_CI):
        """Returns TableDefinition object from parsed metadata-records

        The method uses
        :tableausdk:`Tableau Extract <classtableausdk_1_1_extract_1_1_extract>`
        module to create Table Definition object from parsed column
        information from the datasource file.

        Parameters
        ----------
        collation : :py:attr:`~tableausdk.Types.Collation`, optional
            collation to be used for all columns of the table
            (default value is :py:attr:`~tableausdk.Types.Collation.EN_US_CI`)

        Returns
        -------
        :tableausdk:`TableDefinition \
        <classtableausdk_1_1_extract_1_1_table_definition>`

        Raises
        ------
        :tableausdk:`TableauException \
        <classtableausdk_1_1_exceptions_1_1_tableau_exception>`

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

        for i, col_def in enumerate(column_definitions, start=1):
            parent_name = col_def.get(TDSContentHandler.K_COL_DEF_PARENT_NAME)
            local_name = col_def.get(TDSContentHandler.K_COL_DEF_LOCAL_NAME)
            local_type = col_def.get(TDSContentHandler.K_COL_DEF_LOCAL_TYPE)

            assert_msg = err_msgs.IS_NONE + 'at: {}: {!s}\n'

            assert parent_name is not None, assert_msg.format(
                TDSContentHandler.K_COL_DEF_PARENT_NAME, i, col_def
            )

            assert local_name is not None, assert_msg.format(
                TDSContentHandler.K_COL_DEF_LOCAL_NAME, i, col_def
            )

            assert local_type is not None, assert_msg.format(
                TDSContentHandler.K_COL_DEF_LOCAL_TYPE, i, col_def
            )

            column_name = '{}.{}'.format(parent_name, local_name)
            column_type = self._type_map.get(
                local_type,
                self._type_map['unicode_string']
            )

            table_definition.addColumn(column_name, column_type)

        return table_definition

    def get_datasource_column_defs(self):
        """Gets tableau datasource column information

        Returns
        -------
        TDSContentHandler.column_definitions
            column information of datasource file read

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
        """Gets tableau datasource metadata information

        Returns
        -------
        TDSContentHandler.metadata
            metadata information of datasource file read

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
        """Reads tableau datasource file into `xml_content_handler`

        Parameters
        ----------
        tds_file : str
            path to tableau datasource file


        Raises
        ------
        ReaderException
            when `tds_file` is not parsable or readable

        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')
        """

        super(TDSReader, self).check_file_readable(tds_file)

        try:
            absolute_path = str(Path(tds_file).resolve())
            tree = etree.parse(absolute_path, parser=self._parser)
            root = tree.getroot()

            self._xml_content_handler.parse(root)
        except (etree.XMLSchemaParseError, ContentHandlerException) as err:
            reraise(ReaderException, str(err), sys.exc_info()[2])
