# -*- coding: utf-8 -*-

"""
Unit Test Cases for content_handlers module

Classes:

    TestTDSContentHandler

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
from copy import deepcopy
import yaml
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

    def test_parse_stale_value(self):
        """
        Asserts:
            * metadata property when already containting values after error remains same
            * column definition property when already containing values after error remains same

        """
        tds_xml = etree.parse('sample/sample.tds').getroot()

        try:
            self.content_handler.parse(tds_xml)
        except AssertionError:
            self.fail('parse() raised AssertionError unexpectedly')

        metadata = self.content_handler.metadata
        column_definitions = self.content_handler.column_definitions

        tds_xml = etree.Element('element')

        with self.assertRaises(AssertionError):
            self.content_handler.parse(tds_xml)

        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        self.assertDictEqual(metadata, self.content_handler.metadata)

        self.assertIsNotNone(column_definitions)
        self.assertIsInstance(column_definitions, list)
        self.assertListEqual(column_definitions, self.content_handler.column_definitions)

    def test_metadata(self):
        """
        Asserts:
            * Metadata is not None after parse
            * Metadata is instance of dict after parse
            * Metadata has 2 keys: datasource and connection after parse
            * Metadata:datasource and Metadata:connection are instances of dict after parse
            * Metadata:datasource and Metadata:connection are not empty after parse
            * Metadata information is equal to expected value after parse

        """
        tds_xml = etree.parse('sample/sample.tds').getroot()
        self.content_handler.parse(tds_xml)

        metadata = self.content_handler.metadata

        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        self.assertEqual(len(metadata), 2)

        self.assertTrue(metadata.has_key('datasource'))
        self.assertIsInstance(metadata['datasource'], dict)
        self.assertFalse(len(metadata['datasource']) == 0)

        self.assertTrue(metadata.has_key('connection'))
        self.assertIsInstance(metadata['connection'], dict)
        self.assertFalse(len(metadata['connection']) == 0)

        with open('tests/resources/sample-datasource-metadata-definition.yaml', 'r') as stream:
            expected_result = yaml.load(stream)
            self.assertDictEqual(metadata, expected_result)

    def test_column_definitions(self):
        """
        Asserts:
            * Column Definitions is not None after parse
            * Column Definitions is instance of list after parse
            * Column Definitions has expected length equal to column length in datasource
            * Column Definitions each element is a dict
            * Column Definitions each element has 3 keys namely local-name, parent-name, local-type
            * Column Definitions each element each key value is instance of str
            * Column Definitions value is equal to expected value

        """
        tds_xml = etree.parse('sample/sample.tds').getroot()
        self.content_handler.parse(tds_xml)

        column_definitions = self.content_handler.column_definitions

        self.assertIsNotNone(column_definitions)
        self.assertIsInstance(column_definitions, list)
        self.assertEqual(len(column_definitions), 9)

        for definition in column_definitions:
            self.assertIsInstance(definition, dict)

            self.assertTrue(definition.has_key('local-name'))
            self.assertTrue(definition.has_key('parent-name'))
            self.assertTrue(definition.has_key('local-type'))

            self.assertIsInstance(definition['local-name'], str)
            self.assertIsInstance(definition['parent-name'], str)
            self.assertIsInstance(definition['local-type'], str)

        with open('tests/resources/sample-datasource-column-definitions.yaml', 'r') as stream:
            expected_result = yaml.load(stream)
            self.assertListEqual(column_definitions, expected_result)


if __name__ == '__main__':
    unittest.main()
