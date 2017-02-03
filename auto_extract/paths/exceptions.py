# -*- coding: utf-8 -*-
from auto_extract.paths._paths import VERSIONS

class NoMatchingVersionFound(LookupError):
    """
    Tableau Version not found exception
    """

    message = 'unexpected version found'

    def __init__(self, version):
        super(NoMatchingVersionFound, self).__init__()
        self.version = version

    def __str__(self):
        return '{!r}: {}. Expected: {}'.format(
            self.version,
            self.message,
            VERSIONS
        )


class PathLookupError(KeyError):
    """When an unexpected path key is given for lookup"""

    message = 'path not found'

    def __init__(self, path_key):
        super(PathLookupError, self).__init__(path_key)
        self.path_key = path_key

    def __str__(self):
        return '{!r}: {}'.format(self.path_key, self.message)


class UnexpectedParentInTableauPath(Exception):
    """When a path is being looked up from an unexpected xml element"""

    message = 'path is being looked up from an unexpected parent'

    def __init__(self, parent, expected_parents):
        super(UnexpectedParentInTableauPath, self).__init__(parent)
        self.parent = parent
        self.expected_parents = expected_parents

    def __str__(self):
        return '{!r}: {}. Expected: {}'.format(
            self.parent,
            self.message,
            self.expected_parents
        )
