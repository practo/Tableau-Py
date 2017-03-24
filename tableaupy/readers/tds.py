# -*- coding: utf-8 -*-
"""This module defines tableau datasource xml reader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future.utils import raise_with_traceback
import lxml.etree as etree
from pathlib2 import Path

from tableaupy.contenthandlers import ContentHandlerException
from tableaupy.readers.base import Reader
from tableaupy.readers.exceptions import ReaderException


class TDSReader(Reader):
    """Reader class for Tableau datasource files (\\*.tds)

    Parameters
    ----------
    xml_content_handler : TDSContentHandler
        content handler to parse information from tableau datasource
        parsed information will be saved in this object
    """

    _parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

    def __init__(self, xml_content_handler):
        super(TDSReader, self).__init__('.tds')
        self._xml_content_handler = xml_content_handler

    def get_datasource_column_defs(self):
        """Gets tableau datasource column information

        Returns
        -------
        TDSContentHandler.column_definitions
            column information of datasource file read

        Examples
        --------
        >>> from tableaupy.contenthandlers import TDSContentHandler
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
        >>> from tableaupy.contenthandlers import TDSContentHandler
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
        >>> from tableaupy.contenthandlers import TDSContentHandler
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
            raise_with_traceback(ReaderException(err))
