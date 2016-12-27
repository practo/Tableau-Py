# -*- coding: utf-8 -*-
"""
This module defines status constants
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from auto_extract import _color

#: Success status
SUCCESS = {
    'text': 'Success',
    'color': _color.GREEN
}

#: Failed status
FAILED = {
    'text': 'Failed',
    'color': _color.RED
}
