# -*- coding: utf-8 -*-
"""Exceptions for Tableau Readers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class ReaderException(Exception):
    """raised when an exception is thrown by a Reader"""

    def __init__(self, *args, **kwargs):
        super(ReaderException, self).__init__(*args, **kwargs)
