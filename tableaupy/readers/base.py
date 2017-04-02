# -*- coding: utf-8 -*-
"""This module defines tableau file reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from future.utils import raise_with_traceback
import lxml.etree as etree
from pathlib2 import Path

from tableaupy.contenthandlers import ContentHandlerException
from tableaupy.readers import exceptions


class Reader(object):
    """Base class for all readers"""

    _parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

    def __init__(self, extension, content_handler):
        super(Reader, self).__init__()
        self.__extension = extension
        self._xml_content_handler = content_handler()

    @property
    def extension(self):
        """extension getter"""

        return self.__extension

    def read(self, file_path):
        """Reads and parses the content of the file

        Parameters
        ----------
        file_path : str
            path to file to be read and parsed


        Raises
        ------
        FileNotFound
            when file does not exists
        NodeNotFile
            when `file_path` is not a file
        FileNotReadable
            when file is not readable
        FileExtensionMismatch
            when extension in file name does not match with desired extension
        ReaderException
            when not able to parse file
        """

        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise exceptions.FileNotFound(filename=str(file_path))

            absolute_path = str(file_path.resolve())

            if not file_path.is_file():
                raise exceptions.NodeNotFile(filename=str(file_path))

            if not os.access(absolute_path, os.R_OK):
                raise exceptions.FileNotReadable(filename=file_path)

            if file_path.suffix != self.__extension:
                raise exceptions.FileExtensionMismatch(
                    filename=str(file_path),
                    extension=self.__extension
                )

            tree = etree.parse(absolute_path, parser=self._parser)
            root = tree.getroot()

            self._xml_content_handler.parse(root)
        except (etree.XMLSchemaParseError, ContentHandlerException) as err:
            raise_with_traceback(exceptions.ReaderException(err))
