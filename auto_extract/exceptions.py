# -*- coding: utf-8 -*-
"""This module defines exceptions for auto_extract package
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
