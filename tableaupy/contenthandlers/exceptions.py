# -*- coding: utf-8 -*-
"""Exceptions for Tableau Content Handlers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tableaupy.exceptions import TableauPyException


class ContentHandlerException(TableauPyException):
    """raised when an exception is thrown by a ContentHandlers"""

    _message_template = 'An error occurred with ContentHandler'


class UnexpectedCount(ContentHandlerException, AssertionError):
    """raised when an assertion of element count fails after parsing"""

    _message_template = 'expected count of {} to be {}, got {}'

    def __init__(self, identifier, expected, value):
        AssertionError.__init__(self)
        ContentHandlerException.__init__(self)

        self.identifier = identifier
        self.expected_count = expected
        self.count_value = value

        self.args += (identifier, expected, value)


class UnexpectedEmptyInformation(ContentHandlerException, AssertionError):
    """raised when assertion of non empty array/object fails after parsing"""

    _message_template = '{!r}: information is empty'

    def __init__(self, identifier):
        AssertionError.__init__(self)
        ContentHandlerException.__init__(self)

        self.identifier = identifier

        self.args += (identifier,)
