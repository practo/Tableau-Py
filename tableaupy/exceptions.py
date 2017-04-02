# -*- coding: utf-8 -*-
# pylint: disable=too-many-ancestors

"""This module defines exceptions for tableaupy package
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class AutoExtractException(Exception):
    """AutoExtract Command exception"""
    pass


class TableauPyException(Exception):
    """Base TableauPy exception"""

    _message_template = 'A TableauPy exception has occurred'

    def __init__(self, cause=None):
        Exception.__init__(self)
        self.cause = cause

    def __str__(self):
        if self.cause is None:
            return self._message_template.format(*self.args)
        else:
            return str(self.cause)


class FileIOException(TableauPyException, IOError):
    """Base FileIOException thrown for file input/output exceptions"""

    _message_template = 'An error occurred while reading/writing file: {!r}'

    def __init__(self, filename):
        IOError.__init__(self)
        TableauPyException.__init__(self)
        # using filename attribute reports wrong result
        # thus using file here
        self.file = filename
        self.args += (filename,)


class UnexpectedNoneValue(TableauPyException, AssertionError):
    """Exception is thrown when a value is unexpectedly None"""

    _message_template = '{} is None'

    def __init__(self, identifier):
        AssertionError.__init__(self)
        TableauPyException.__init__(self)
        self.identifier = identifier
        self.args += (identifier,)
