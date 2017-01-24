# -*- coding: utf-8 -*-
"""Exceptions for Tableau Writers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class WriterException(Exception):
    """raised when an exception is thrown by a Writer"""

    def __init__(self, *args, **kwargs):
        super(WriterException, self).__init__(*args, **kwargs)
