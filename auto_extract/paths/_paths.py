# -*- coding: utf-8 -*-
from __future__ import absolute_import

from semantic_version import Version
from auto_extract.paths import constants


class _TableauPath(object):
    """
    TableauPath class

    Properties
    ----------
    xpath: str
    parent: list
        list of tags to expect for a given xpath
        if in lookup xml.tag is not in the list
        `UnexpectedParentInTableauPath` is raised
    """

    def __init__(self, xpath, parents):
        super(_TableauPath, self).__init__()
        self._xpath = xpath
        self._parents = list(parents)

    @property
    def parents(self):
        """TableauPath parents property"""
        return self._parents

    @property
    def xpath(self):
        """TableauPath xpath property"""
        return self._xpath


BASE_PATHS = {
    constants.TDS_CONNECTION: _TableauPath(
        'connection',
        ['datasource']
    ),
    constants.TDS_METADATA_RECORD: _TableauPath(
        'connection/metadata-records/metadata-record',
        ['datasource']
    )
}

VERSION_PATHS = {
    '10.0': {
        constants.TDS_CONNECTION: _TableauPath(
            'connection/named-connections/named-connection/connection',
            ['datasource']
        )
    },
}

VERSIONS = sorted(
    VERSION_PATHS.keys(),
    key=lambda x: Version(x, partial=True),
    reverse=True
)
