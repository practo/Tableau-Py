# -*- coding: utf-8 -*-
# pylint: disable=too-many-ancestors

"""Exceptions for Tableau Writers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tableaupy import exceptions


class WriterException(exceptions.TableauPyException):
    """raised when an exception is thrown by a Writer"""

    _message_template = 'An error occurred with Writer'


class FileOutputException(exceptions.FileIOException, WriterException):
    """raised when an exception occurs while writing file for Writer"""

    _message_template = 'An error occurred while writing file: {!r}'


class FileAlreadyExists(FileOutputException):
    """raised when file to be written by Writer already exists

    The exception is thrown only if, the overwriting file in anyway
    is not permissible
    """

    _message_template = '{!r}: file already exists'
