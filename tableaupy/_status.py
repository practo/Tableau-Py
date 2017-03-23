# -*- coding: utf-8 -*-
"""This module defines status constants
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tableaupy import _color


class Status(dict):
    """Status class

    Defines the result status for tableaupy command

    Attributes
    ----------
    text : str
        text to display
    color : str
        background color of the text
    """

    def __init__(self, text, color):
        super(Status, self).__init__()
        self['color'] = color
        self['text'] = text

    @property
    def color(self):
        """color property"""
        return self['color']

    @property
    def text(self):
        """text property"""
        return self['text']


#: Success status
SUCCESS = Status('Success', _color.GREEN)

#: Failed status
FAILED = Status('Failed', _color.RED)
