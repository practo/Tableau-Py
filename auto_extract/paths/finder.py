# -*- coding: utf-8 -*-
from __future__ import absolute_import

from itertools import ifilter
from semantic_version import Version
from semantic_version import Spec
from auto_extract.paths import exceptions
from auto_extract.paths import _paths


def get_nearest_version(version):
    """
    Gets nearest guessed version to available path versions

    Parameters
    ----------
    version : str
        version from which nearest version is to be get

    Returns
    -------
    str or None,
        nearest version or else returns None if not found

    """
    ver_obj = Version(version, partial=True)
    ver_filter = ifilter(lambda v: ver_obj in Spec('^' + v), _paths.VERSIONS)
    ver_obj = next(ver_filter, None)

    return str(ver_obj) if ver_obj is not None else None


def get_xpath(xml, path, strict=True):
    """
    Gets xpath for an xml element

    It looks up the root of the element to identify the version,
    if version is not found base version is assumed.

    When `strict` is True, version should match the versions
    expected by the module or else an error will be thrown

    When `strict` is False or None, method tries to guess the version,
    if it fails to guess, an error is thrown

    Parameters
    ----------
    xml : :py:obj:`~lxml.etree.Element`
        element to get the path for
    path : str
        path keys available as public constants of this module
    strict : bool
        if true match exact version else match `^` version

    Returns
    -------
    str
        xpath for xml element

    Raises
    ------
    NoMatchingVersionFound
        when `strict` is True and root element doesn't have an expected version
    PathLookupError
        when an unexpected path key is given for a xpath
    UnexpectedParentInTableauPath
        when a path key is given from an unexpected parent
    """

    version = None
    tableau_path = None

    root = xml.getroottree().getroot()

    if root.get('version'):
        version = root.get('version')

        if strict and version not in _paths.VERSIONS:
            raise exceptions.NoMatchingVersionFound('unknown version: {!r}' % version)

        if not strict and version not in _paths.VERSIONS:
            version = get_nearest_version(version)

        if version is not None and _paths.VERSION_PATHS[version].get(path):
            tableau_path = _paths.VERSION_PATHS[version].get(path)

    if tableau_path is None and _paths.BASE_PATHS.get(path):
        tableau_path = _paths.BASE_PATHS.get(path)

    if tableau_path is None:
        raise exceptions.PathLookupError(path)

    if xml.tag not in tableau_path.parents:
        raise exceptions.UnexpectedParentInTableauPath(xml.tag, tableau_path.parents)

    return tableau_path.xpath


def get_count_path(xml, path, strict=True):
    """
    Translates an xpath to return count of elements
    returned by xpath

    Parameters
    ----------
    xml : :py:obj:`~lxml.etree.Element`
        element to get the path for
    path : str
    strict : bool
        if true match exact version
        else match `^` version

    Returns
    -------
    str
        xpath that count elements in xpath
    """
    xpath = get_xpath(xml, path, strict)
    return 'count({})'.format(xpath)


def get_name_path(xml, path, strict=True):
    """
    Translates an xpath to return the names of elements
    returned by xpath

    Parameters
    ----------
    xml : :py:obj:`~lxml.etree.Element`
        element to get the path for
    path : str
    strict : bool
        if true match exact version
        else match `^` version

    Returns
    -------
    str
        xpath that returns @name attribute values
    """
    xpath = get_xpath(xml, path, strict)
    return '{}/@name'.format(xpath)
