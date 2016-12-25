# -*- coding: utf-8 -*-
"""
This module defines exceptions for auto_extract package

"""


class AutoExtractException(Exception):
    """
    AutoExtract Command exception

    """

    def __init__(self, *args, **kwargs):
        super(AutoExtractException, self).__init__(*args, **kwargs)
