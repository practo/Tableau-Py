# -*- coding: utf-8 -*-

"""
Unit Test Cases for content_handlers module

Classes:

    TestTDSContentHandler

"""
from __future__ import absolute_import

import unittest
from copy import deepcopy
from auto_extract.content_handlers import TDSContentHandler
import lxml.etree as etree


class TestTDSContentHandler(unittest.TestCase):
    """
    Unit Test Cases for testing TDSContentHandler

    """

    def setUp(self):
        self.content_handler = TDSContentHandler()
        self.maxDiff = None  # pylint: disable=locally-disabled,invalid-name

    def tearDown(self):
        self.content_handler = None

    def _check_error(self, tds_xml, regex_match):
        """
        Checks if parsing `tds_xml` gives assertion error matching `regex_match`
        Further assertions are used to check if there is any stale information being,
        stored in the method properties

        Asserts:
            * Raises given error
            * If after raise metadata property is not None
            * If after raise metadata property is an instance of dict
            * If after raise metadata property is empty dict
            * If after raise column_definitions property is not None
            * If after raise column_definitions property is an instance of list
            * If after raise column_definitions property is empty list

        """
        with self.assertRaisesRegexp(AssertionError, regex_match):
            self.content_handler.parse(tds_xml)

        self.assertIsNotNone(self.content_handler.metadata)
        self.assertIsInstance(self.content_handler.metadata, dict)
        self.assertEqual(self.content_handler.metadata, {})

        self.assertIsNotNone(self.content_handler.column_definitions)
        self.assertIsInstance(self.content_handler.column_definitions, list)
        self.assertEqual(self.content_handler.column_definitions, [])

    def _fail_on_missing_datasource_information(self, tds_xml):  # pylint: disable=locally-disabled,invalid-name
        """
        Checks if parsing `tds_xml` without datasource information
        gives assertion error

        """
        self._check_error(tds_xml, 'datasource information is empty')

    def _fail_on_missing_inside_connection(self, tds_xml):  # pylint: disable=locally-disabled,invalid-name
        """
        Checks if parsing `tds_xml` without connection information
        gives assertion error

        """
        self._check_error(tds_xml, 'expected number of connections to be 1, got 0')

    def _fail_on_multiple_connections(self, tds_xml, element):  # pylint: disable=locally-disabled,invalid-name
        """
        Checks if parsing `tds_xml` with multiple connection information
        gives assertion error. It duplicates `element` as a sibling to it's parent
        to repeat the inside connection.

        """
        parent = element.getparent()
        element_copy = deepcopy(element)
        parent.append(element_copy)
        self._check_error(tds_xml, 'expected number of connections to be 1, got 2')
        parent.remove(element_copy)

    def test_parse_without_datasource_information(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * When datasource is not the root object
            * When datasource is the root object without attributes
            * When datasource is the root object with attributes

        """
        tds_xml = etree.Element('test')
        self._fail_on_missing_datasource_information(tds_xml)

        tds_xml = etree.Element('datasource')
        self._fail_on_missing_datasource_information(tds_xml)

        tds_xml.attrib.update({
            'inline': 'true',
            'formatted-name': 'Datasource Testing',
        })
        self._fail_on_missing_inside_connection(tds_xml)

    def test_parse_without_inside_connection_information(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * When datasource is not having connection element
            * When connection is not having named-connections element
            * When named-connections is not having named-connection element
            * When named-connection is not having inside `connection` element
            * When inside connection element does not have attributes
            * When inside connection element have attributes

        """
        tds_xml = etree.Element('datasource')
        tds_xml.attrib.update({
            'inline': 'true',
            'formatted-name': 'Datasource Testing',
        })

        connection = etree.Element('connection')
        tds_xml.append(connection)
        self._fail_on_missing_inside_connection(tds_xml)

        named_connections = etree.Element('named-connections')
        connection.append(named_connections)
        self._fail_on_missing_inside_connection(tds_xml)

        named_connection = etree.Element('named-connection')
        named_connections.append(named_connection)
        self._fail_on_missing_inside_connection(tds_xml)

        connection_inside = etree.Element('connection')
        named_connection.append(connection_inside)

        with self.assertRaisesRegexp(AssertionError, 'connection information is empty'):
            self.content_handler.parse(tds_xml)

        connection_inside.attrib.update({
            'server': '0.0.0.0'
        })

        try:
            self.content_handler.parse(tds_xml)
        except AssertionError:
            self.fail('parse() raised AssertionError unexpectedly')

    def test_parse_with_multiple_connections(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * When named-connection has more than one inside connection
            * When named-connections has more than one named-connection with connection inside
            * When connection has more than one named-connections with connection inside
            * When datasource has more than one connection with connection inside
            * When datasource has only one connection inside with connection inside

        """
        tds_xml = etree.Element('datasource')
        tds_xml.attrib.update({
            'inline': 'true',
            'formatted-name': 'Datasource Testing',
        })

        connection = etree.Element('connection')
        tds_xml.append(connection)

        named_connections = etree.Element('named-connections')
        connection.append(named_connections)

        named_connection = etree.Element('named-connection')
        named_connections.append(named_connection)

        connection_inside = etree.Element('connection')
        named_connection.append(connection_inside)

        connection_inside.attrib.update({
            'server': '0.0.0.0'
        })

        self._fail_on_multiple_connections(tds_xml, connection_inside)
        self._fail_on_multiple_connections(tds_xml, named_connection)
        self._fail_on_multiple_connections(tds_xml, named_connections)
        self._fail_on_multiple_connections(tds_xml, connection)

        try:
            self.content_handler.parse(tds_xml)
        except AssertionError:
            self.fail('parse() raised AssertionError unexpectedly')


if __name__ == '__main__':
    unittest.main()