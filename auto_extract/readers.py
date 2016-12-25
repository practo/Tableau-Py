# -*- coding: utf-8 -*-
"""
This module defines xml readers for tableau files

"""

from __future__ import absolute_import, print_function, unicode_literals
import os

from pathlib2 import Path
from tableausdk.Types import Type, Collation
from tableausdk.Extract import TableDefinition
import lxml.etree as etree


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
            parent_name = definition.get('parent-name')
            local_name = definition.get('local-name')
            local_type = definition.get('local-type')

            assert parent_name is not None, 'parent-name is None at: {}:\n'.format(i) + str(definition)
            assert local_name is not None, 'local-name is None at: {}:\n'.format(i) + str(definition)
            assert local_type is not None, 'local-type is None at: {}:\n'.format(i) + str(definition)

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
        >>> tds_reader.get_datasource_column_defs() == tds_content_handler.column_definitions
        True

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
        >>> tds_reader.get_datasource_metadata() == tds_content_handler.metadata
        True

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
        OSError
            when `tds_file` is not readable
        :py:exc:`~lxml.etree.XMLSchemaParseError`
            when `tds_file` is not xml parsable


        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('some random file') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        IOError: does not exists

        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        IOError: not a file

        """
        tds_file_path = Path(tds_file)

        if not tds_file_path.exists():
            raise IOError('does not exists')

        absolute_path = str(tds_file_path.resolve())

        if not tds_file_path.is_file():
            raise IOError('not a file')

        if not os.access(absolute_path, os.R_OK):
            raise IOError('not readable')

        if tds_file_path.suffix != '.tds':
            raise IOError('does not have extension `.tds`')

        tree = etree.parse(absolute_path, parser=self._parser)
        root = tree.getroot()

        self._xml_content_handler.parse(root)
