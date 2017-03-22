# -*- coding: utf-8 -*-
"""This module defines tableau file reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from pathlib2 import Path

from auto_extract.readers import exceptions


class Reader(object):
    """Base class for all readers"""

    def __init__(self, extension):
        super(Reader, self).__init__()
        self.extension = extension

    def check_file_readable(self, file_name):
        """Checks if `file_name` is readable

        Parameters
        ----------
        file_name : str
            path to file_name to read

        Raises
        ------
        ReaderException
            when `file_name` is not readable or doesn't have expected extension
        """

        file_path = Path(file_name)

        if not file_path.exists():
            raise exceptions.FileNotFound(filename=file_name)

        absolute_path = str(file_path.resolve())

        if not file_path.is_file():
            raise exceptions.NodeNotFile(filename=file_name)

        if not os.access(absolute_path, os.R_OK):
            raise exceptions.FileNotReadable(filename=file_name)

        if file_path.suffix != self.extension:
            raise exceptions.FileExtensionMismatch(
                filename=file_name,
                extension=self.extension
            )
