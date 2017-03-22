# -*- coding: utf-8 -*-
# pylint: disable=too-many-ancestors

"""Exceptions for Tableau Readers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from auto_extract import exceptions


class ReaderException(exceptions.TableauPyException):
    """raised when an exception is thrown by a Reader"""

    _message_template = 'An error occurred with Reader'


class FileInputException(exceptions.FileIOException, ReaderException):
    """raised when an exception occurs while reading file for Reader"""

    _message_template = 'An error occurred while reading file: {!r}'


class FileNotFound(FileInputException):
    """raised when input file to be read does not exists"""

    _message_template = '{!r}: file does not exists'


class FileNotReadable(FileInputException):
    """raised when input file to be read does not have read permissions"""

    _message_template = '{!r}: not readable'


class NodeNotFile(FileInputException):
    """raised when input path given as file to be read is not of a file"""

    _message_template = '{!r}: not a file'


class FileExtensionMismatch(FileInputException):
    """raised when input file extension mismatches expected Reader extension"""

    _message_template = '{!r}: does not have extension `{}`'

    def __init__(self, filename, extension):
        FileInputException.__init__(self, filename=filename)
        self.extension = extension
        self.args += (extension,)
