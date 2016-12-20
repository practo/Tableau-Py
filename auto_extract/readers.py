# -*- coding: utf-8 -*-
"""
This module defines xml readers for tableau files

Readers
-------
    - `TDSReader`

"""

from __future__ import absolute_import, print_function, unicode_literals

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

    def __init__(self, xml_content_handler):
        super(TDSReader, self).__init__()
        self._xml_content_handler = xml_content_handler

    def define_table(self):
        """
        Creates a `TableauDefinition` object from the column information returned after parsing
        the tableau datasource file

        Returns
        -------
        :py:exc:`~tableausdk.Extract.TableauDefinition`

        Raises
        ------
        :py:exc:`~tableausdk.Exceptions.TableauException`

        """
        pass

    def get_datasource_columns(self):
        """
        Returns read tableau datasource column information

        Returns
        -------
        TDSContentHandler.columns

        """
        tds_content = self._xml_content_handler

        return tds_content.columns

    def get_datasource_metadata(self):
        """
        Returns read tableau datasource metadata information

        Returns
        -------
        TDSContentHandler.metadata

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
        :py:exc:`IOError`
            when `tds_file` is not readable
        :py:exc:`~lxml.etree.XMLSchemaParseError`
            when `tds_file` is not xml parsable

        """
        pass
