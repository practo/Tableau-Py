# -*- coding: utf-8 -*-
"""Exceptions for Tableau Content Handlers"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class ContentHandlerException(Exception):
    """raised when an exception is thrown by a ContentHandlers"""

    def __init__(self, *args, **kwargs):
        super(ContentHandlerException, self).__init__(*args, **kwargs)
