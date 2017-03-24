# -*- coding: utf-8 -*-
"""This module defines tableau file writer base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pathlib2 import Path
from future.utils import raise_with_traceback

from tableaupy.writers import exceptions


class Writer(object):
    """Writer class

    Parameters
    ----------
    extension: str
        extension
    options: dict
        writer options in format::

            {
                prefix: before every output file name (default: ''),
                suffix: after every output file name (default: ''),
                overwrite: a file if exists (default: False),
                output_dir: relative path to output directory for output files
                            when None (default Value), follows writer default
                            behaviour
            }

    Raises
    ------
    OSError
        if output_dir doesn't exists
    """

    def __init__(self, extension, options=None):
        super(Writer, self).__init__()

        self.__extension = extension

        _options = {
            'prefix': '',
            'suffix': '',
            'overwrite': False,
            'output_dir': None,
        }
        _options.update({} if options is None else options)

        self._prefix = _options.get('prefix')
        self._suffix = _options.get('suffix')
        self._overwrite = _options.get('overwrite')
        self._output_dir = _options.get('output_dir')

        if self._output_dir is not None:
            Path(self._output_dir).resolve()

    @property
    def extension(self):
        """extension getter"""

        return self.__extension

    @property
    def prefix(self):
        """prefix getter"""

        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        """prefix setter"""

        self._prefix = prefix

    @property
    def suffix(self):
        """suffix getter"""

        return self._suffix

    @suffix.setter
    def suffix(self, suffix):
        """suffix setter"""

        self._suffix = suffix

    @property
    def overwrite(self):
        """overwrite getter"""

        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite):
        """overwrite setter"""

        self._overwrite = overwrite

    @property
    def output_dir(self):
        """output directory getter"""

        return self._output_dir

    @output_dir.setter
    def output_dir(self, output_dir):
        """output directory setter"""

        self._output_dir = output_dir

    def get_output_path(self, file_path):
        """Returns the absolute path to output file

        Parameters
        ----------
        file_path: str
            path to output file

        Returns
        -------
        str
            absolute path to output file with prefix, suffix
            extension.extension
             and output directory

        Raises
        ------
        WriterException
            when not able to resolve absolute path to output file
        """

        try:
            file_path = Path(file_path)
            output_file_name = self._prefix + file_path.stem + self._suffix
            output_path = file_path.with_name(output_file_name)
            output_path = output_path.with_suffix(self.__extension)

            if self._output_dir is not None:
                output_dir = Path(self._output_dir).resolve()
            else:
                # because the file_path may have been passed with folder name
                output_dir = output_path.parent.resolve()

            return str(output_dir / output_path.name)
        except OSError as err:
            raise_with_traceback(exceptions.WriterException(err))

    def check_file_writable(self, output_path):
        """Checks if the file is writable

        If overwrite is true, overwrites the file
        else if the file exists throws exception

        Parameters
        ----------
        output_path
            path to output file

        Raises
        ------
        WriterException
            if output_path is not writable or already exists

        """
        output_path = Path(output_path)

        if not self._overwrite and output_path.exists():
            raise exceptions.FileAlreadyExists(str(output_path))

        if self._overwrite and output_path.exists():
            Path(output_path).unlink()
