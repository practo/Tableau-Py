# -*- coding: utf-8 -*-
"""Unit Test Cases for TDSContentHandler"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from copy import deepcopy
import unittest

import lxml.etree as etree
import yaml

import config
from tableaupy.contenthandlers import ContentHandlerException
from tableaupy.contenthandlers import TDSContentHandler


class TestTDSContentHandler(unittest.TestCase):
    """Unit Test Cases for testing TDSContentHandler"""

    maxDiff = None

    def setUp(self):
        self.content_handler = TDSContentHandler()

    def tearDown(self):
        self.content_handler = None

    def _check_error(self, tds_xml, regex_match):
        """checks common assertion errors based on params passed

        Checks if parsing `tds_xml` gives assertion error matching
        `regex_match`.

        Further assertions are used to check if there is any stale
        or inconsistent information stored in method properties after parse.

        Asserts
        -------
        * raises ContentHandlerException with regex_match
        * after raise metadata property is not None
        * after raise metadata property is an instance of dict
        * after raise metadata property is empty dict
        * after raise column_definitions property is not None
        * after raise column_definitions property is an instance of list
        * after raise column_definitions property is empty list
        """

        with self.assertRaisesRegexp(ContentHandlerException, regex_match):
            self.content_handler.parse(tds_xml)

        self.assertIsNotNone(self.content_handler.metadata)
        self.assertIsInstance(self.content_handler.metadata, dict)
        self.assertEqual(self.content_handler.metadata, {})

        self.assertIsNotNone(self.content_handler.column_definitions)
        self.assertIsInstance(self.content_handler.column_definitions, list)
        self.assertEqual(self.content_handler.column_definitions, [])

    def _fail_on_missing_datasource_information(self, tds_xml):  # pylint: disable=locally-disabled,invalid-name
        """checks if fails on missing datasource information

        Checks if parsing `tds_xml` without datasource information
        gives assertion error
        """

        self._check_error(tds_xml, '\'datasource\': information is empty')

    def _fail_on_missing_inside_connection(self, tds_xml):  # pylint: disable=locally-disabled,invalid-name
        """checks if fails on missing connection information

        Checks if parsing `tds_xml` without connection information
        gives assertion error
        """

        message = 'expected count of connection to be 1, got 0'
        self._check_error(tds_xml, message)

    def _fail_on_multiple_connections(self, tds_xml, element):  # pylint: disable=locally-disabled,invalid-name
        """checks if fail on multiple connections

        Checks if parsing `tds_xml` with multiple connection information
        gives assertion error.

        It duplicates `element` as a sibling to it's parent to repeat the
        inside connection.
        """

        message = 'expected count of connection to be 1, got 2'
        parent = element.getparent()
        element_copy = deepcopy(element)
        parent.append(element_copy)
        self._check_error(tds_xml, message)
        parent.remove(element_copy)

    def test_parse_without_datasource_information(self):  # pylint: disable=locally-disabled,invalid-name
        """when datasource information is empty

        Asserts
        -------
        * when datasource is not the root object
        * when datasource is the root object without attributes
        * when datasource is the root object with attributes
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
        """when connection information is empty

        Asserts
        -------
        * when datasource is not having connection element
        * when connection is not having named-connections element
        * when named-connections is not having named-connection element
        * when named-connection is not having inside `connection` element
        * when inside connection element does not have attributes
        * when inside connection element have attributes
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

        message = '\'connection\': information is empty'
        with self.assertRaisesRegexp(ContentHandlerException, message):
            self.content_handler.parse(tds_xml)

        connection_inside.attrib.update({
            'server': '0.0.0.0'
        })

        try:
            self.content_handler.parse(tds_xml)
        except ContentHandlerException:
            self.fail('parse() raised ContentHandlerException unexpectedly')

    def test_parse_with_multiple_connections(self):  # pylint: disable=locally-disabled,invalid-name
        """when multiple connections are given

        Asserts
        -------
        * when named-connection has multiple connection
        * when named-connections has multiple named-connection with connection
        * when connection has more than one named-connections
        * when datasource has more than one connection
        * when datasource has only one connection
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
        except ContentHandlerException:
            self.fail('parse() raised ContentHandlerException unexpectedly')

    def test_parse_stale_value(self):
        """to test if stale values are persisted after failed parsing

        Asserts
        -------
        * metadata property doesn't change when interrupted by error
        * column definition property doesn't change when interrupted by error
        """

        tds_xml = etree.parse('sample/sample.tds').getroot()

        try:
            self.content_handler.parse(tds_xml)
        except ContentHandlerException:
            self.fail('parse() raised ContentHandlerException unexpectedly')

        metadata = self.content_handler.metadata
        column_definitions = self.content_handler.column_definitions

        tds_xml = etree.Element('element')

        with self.assertRaises(ContentHandlerException):
            self.content_handler.parse(tds_xml)

        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        self.assertDictEqual(metadata, self.content_handler.metadata)

        self.assertIsNotNone(column_definitions)
        self.assertIsInstance(column_definitions, list)
        self.assertListEqual(
            column_definitions,
            self.content_handler.column_definitions
        )

    def test_metadata(self):
        """to test metadata information after parsing

        Asserts
        -------
        * is not None
        * is dict
        * has 2 keys: datasource, connection
        * values are instances of dict
        * values are not empty
        * is equal to expected result
        """

        tds_xml = etree.parse('sample/sample.tds').getroot()
        self.content_handler.parse(tds_xml)

        metadata = self.content_handler.metadata

        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        self.assertEqual(len(metadata), 2)

        self.assertTrue('datasource' in metadata)
        self.assertIsInstance(metadata['datasource'], dict)
        self.assertFalse(len(metadata['datasource']) == 0)

        self.assertTrue('connection' in metadata)
        self.assertIsInstance(metadata['connection'], dict)
        self.assertFalse(len(metadata['connection']) == 0)

        with open(config.TEST_DS_RESULT_METADATA_PATH, 'r') as stream:
            expected_result = yaml.load(stream)
            self.assertDictEqual(metadata, expected_result)

    def test_column_definitions(self):
        """to test column definition method

        Asserts
        -------
        * is not None
        * is list
        * has length equal to column length in datasource
        * each elemet is a dict
        * each element has keys: local-name, parent-name and local-type
        * each element key values are string
        * is equal to expected result
        """

        tds_xml = etree.parse('sample/sample.tds').getroot()
        self.content_handler.parse(tds_xml)

        column_definitions = self.content_handler.column_definitions

        self.assertIsNotNone(column_definitions)
        self.assertIsInstance(column_definitions, list)
        self.assertEqual(len(column_definitions), 9)

        for definition in column_definitions:
            self.assertIsInstance(definition, dict)

            self.assertTrue('local-name' in definition)
            self.assertTrue('parent-name' in definition)
            self.assertTrue('local-type' in definition)

            self.assertIsInstance(definition['local-name'], unicode)
            self.assertIsInstance(definition['parent-name'], unicode)
            self.assertIsInstance(definition['local-type'], unicode)

        with open(config.TEST_DS_RESULT_COLUMN_DEFINITION_PATH, 'r') as stream:
            expected_result = yaml.load(stream)
            self.assertListEqual(column_definitions, expected_result)


if __name__ == '__main__':
    unittest.main()
