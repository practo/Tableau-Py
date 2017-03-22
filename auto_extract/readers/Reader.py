# -*- coding: utf-8 -*-
"""This module defines tableau file reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from pathlib2 import Path
from six import reraise

from auto_extract import _error_messages as err_msgs
from auto_extract.readers.exceptions import ReaderException


class Reader(object):
    """Base class for all readers"""

    def __init__(self, extension):
        super(Reader, self).__init__()
        self.__extension = extension

    @property
    def extension(self):
        """extension getter"""

        return self.__extension

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

        try:
            if not file_path.exists():
                raise IOError(err_msgs.FILE_NO_EXISTS.format(file_name))

            absolute_path = str(file_path.resolve())

            if not file_path.is_file():
                raise IOError(err_msgs.NOT_FILE.format(file_name))

            if not os.access(absolute_path, os.R_OK):
                raise IOError(err_msgs.NOT_READABLE.format(file_name))

            if file_path.suffix != self.__extension:
                raise IOError(err_msgs.FILE_EXT_NOT_MATCH.format(
                    file_name, self.__extension))
        except IOError as err:
            reraise(ReaderException, str(err), sys.exc_info()[2])
