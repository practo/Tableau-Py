# -*- coding: utf-8 -*-
"""
This module defines xml readers for tableau files

"""

from __future__ import absolute_import, print_function, unicode_literals
import os

from pathlib2 import Path
from tableausdk.Types import Type
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

    def define_table(self):
        """
        Creates a TableDefinition object from the column information returned after parsing
        the tableau datasource file

        Returns
        -------
        :tableausdk:`TableDefinition <classtableausdk_1_1_extract_1_1_table_definition>`

        Raises
        ------
        :tableausdk:`TableauException <classtableausdk_1_1_exceptions_1_1_tableau_exception>`

        """
        pass

    def get_datasource_columns(self):
        """
        Returns read tableau datasource column information

        Returns
        -------
        TDSContentHandler.columns

        Examples
        --------
        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample/sample.tds')
        >>> tds_reader.get_datasource_columns() == tds_content_handler.columns
        True

        """
        tds_content = self._xml_content_handler

        return tds_content.columns

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
        OSError: [Errno 2] No such file or directory: '.../some random file'

        >>> from auto_extract.content_handlers import TDSContentHandler
        >>> tds_content_handler = TDSContentHandler()
        >>> tds_reader = TDSReader(tds_content_handler)
        >>> tds_reader.read('sample') #doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        IOError: not a file

        """
        tds_file_path = Path(tds_file)
        absolute_path = str(tds_file_path.resolve())

        if not tds_file_path.exists():
            raise IOError('does not exists')

        if not tds_file_path.is_file():
            raise IOError('not a file')

        if not os.access(absolute_path, os.R_OK):
            raise IOError('not readable')

        if tds_file_path.suffix != '.tds':
            raise IOError('does not have extension `.tds`')

        tree = etree.parse(absolute_path, parser=self._parser)
        root = tree.getroot()

        self._xml_content_handler.parse(root)
