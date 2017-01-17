# -*- coding: utf-8 -*-
"""Unit Test Cases for TDSReader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

from tableausdk.Extract import TableDefinition
import yaml

from auto_extract.content_handlers import TDSContentHandler
from auto_extract.readers import ReaderException
from auto_extract.readers import TDSReader
import config


class TestTDSReader(unittest.TestCase):
    """
    Unit Test Cases for testing TDSReader

    """

    def setUp(self):
        self.content_handler = TDSContentHandler()
        self.reader = TDSReader(self.content_handler)
        self.maxDiff = None  # pylint: disable=locally-disabled,invalid-name

    def tearDown(self):
        self.content_handler = None
        self.reader = None

    def test_read(self):
        """
        Asserts
        -------
        * Raises ReaderException for missing file / directory
        * Raises ReaderException when file expected but folder or something other
          than file given
        * Raises ReaderException when file given does not have .tds extension in name

        """
        expected_regexp = '\'sample/randome file.tds\': file does not exists'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            test_filename = os.path.join(config.SAMPLE_PATH, 'randome file.tds')
            self.reader.read(test_filename)

        expected_regexp = '\'sample\': not a file'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            self.reader.read(config.SAMPLE_PATH)

        expected_regexp = '\'tox.ini\': does not have extension `.tds`'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            self.reader.read('tox.ini')

    def _assert_metadata(self, metadata, expected_length, expected_value):
        """
        Asserts
        -------
        * Value is not None
        * Value is having expected length
        * Value is instance of dictionary
        * Value is equal to expected value

        """
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), expected_length)
        self.assertIsInstance(metadata, dict)
        self.assertDictEqual(metadata, expected_value)

        self.assertDictEqual(metadata, self.content_handler.metadata)

    def test_get_datasource_metadata(self):
        """
        Asserts
        -------
        * Metadata values before calling read
        * Metadata values after calling read

        """

        self._assert_metadata(self.reader.get_datasource_metadata(), 0, {})

        self.reader.read(config.SAMPLE_DS_PATH)

        with open(config.TEST_DS_RESULT_METADATA_PATH) as stream:
            expected_result = yaml.load(stream)
            self._assert_metadata(self.reader.get_datasource_metadata(), 2, expected_result)

    def _assert_column_definitions(self, column_definitions, expected_length, expected_value):
        """
        Asserts
        -------
        * Value is not None
        * Value is having expected length
        * Value is instance of list
        * Value is equal to expected value

        """
        self.assertIsNotNone(column_definitions)
        self.assertEqual(len(column_definitions), expected_length)
        self.assertIsInstance(column_definitions, list)
        self.assertListEqual(column_definitions, expected_value)

    def test_get_datasource_column_defs(self):
        """
        Asserts
        -------
        * Column definition values before calling read
        * Column definition values after calling read

        """

        self._assert_column_definitions(self.reader.get_datasource_column_defs(), 0, [])

        self.reader.read(config.SAMPLE_DS_PATH)

        with open(config.TEST_DS_RESULT_COLUMN_DEFINITION_PATH) as stream:
            expected_result = yaml.load(stream)
            self._assert_column_definitions(self.reader.get_datasource_column_defs(), 9, expected_result)

    def _assert_table_definition(self, table_def, expected_col_count, expected_collation):
        """
        Asserts
        -------
        * Value is not None
        * Value is instance of TableDefinition
        * Value has expected column count
        * Value has expected default collation
        * Column count should be equal to length of get_datasource_column_defs

        """
        self.assertIsNotNone(table_def)
        self.assertIsInstance(table_def, TableDefinition)
        self.assertEqual(table_def.getColumnCount(), expected_col_count)
        self.assertEqual(table_def.getDefaultCollation(), expected_collation)
        self.assertEqual(
            table_def.getColumnCount(),
            len(self.reader.get_datasource_column_defs())
        )

    def test_define_table(self):
        """
        Asserts
        -------
        * Table Definition value before calling read
        * Table Definition value after calling read
        * Each column in table definition is having the expected name
        * Each column is table definition having the expected type
        * Each column is table definition having expected collation (default collation)

        """
        import re
        import random
        from tableausdk.Types import Collation, Type

        pattern = re.compile('^_.*')
        collation_types = [x for x in vars(Collation).keys() if not pattern.match(x)]
        collation = getattr(Collation, random.choice(collation_types))

        table_definition = self.reader.define_table(collation=collation)
        self._assert_table_definition(table_definition, 0, collation)

        self.reader.read(config.SAMPLE_DS_PATH)

        table_definition = self.reader.define_table(collation=collation)
        self._assert_table_definition(table_definition, 9, collation)

        def col_name(name): return '[{}].[{}]'.format('TABLE_NAME', name)

        get_column_name = table_definition.getColumnName
        get_column_type = table_definition.getColumnType
        get_column_collation = table_definition.getColumnCollation

        self.assertEqual(get_column_name(0), col_name('LOCAL_COLUMN_NAME1'))
        self.assertEqual(get_column_name(1), col_name('LOCAL_COLUMN_NAME2'))
        self.assertEqual(get_column_name(2), col_name('LOCAL_COLUMN_NAME3'))
        self.assertEqual(get_column_name(3), col_name('LOCAL_COLUMN_NAME4'))
        self.assertEqual(get_column_name(4), col_name('LOCAL_COLUMN_NAME5'))
        self.assertEqual(get_column_name(5), col_name('LOCAL_COLUMN_NAME6'))
        self.assertEqual(get_column_name(6), col_name('LOCAL_COLUMN_NAME7'))
        self.assertEqual(get_column_name(7), col_name('LOCAL_COLUMN_NAME8'))
        self.assertEqual(get_column_name(8), col_name('LOCAL_COLUMN_NAME9'))

        self.assertEqual(get_column_type(0), Type.DATE)
        self.assertEqual(get_column_type(1), Type.CHAR_STRING)
        self.assertEqual(get_column_type(2), Type.CHAR_STRING)
        self.assertEqual(get_column_type(3), Type.CHAR_STRING)
        self.assertEqual(get_column_type(4), Type.CHAR_STRING)
        self.assertEqual(get_column_type(5), Type.CHAR_STRING)
        self.assertEqual(get_column_type(6), Type.CHAR_STRING)
        self.assertEqual(get_column_type(7), Type.CHAR_STRING)
        self.assertEqual(get_column_type(8), Type.CHAR_STRING)

        self.assertEqual(get_column_collation(0), collation)
        self.assertEqual(get_column_collation(1), collation)
        self.assertEqual(get_column_collation(2), collation)
        self.assertEqual(get_column_collation(3), collation)
        self.assertEqual(get_column_collation(4), collation)
        self.assertEqual(get_column_collation(5), collation)
        self.assertEqual(get_column_collation(6), collation)
        self.assertEqual(get_column_collation(7), collation)
        self.assertEqual(get_column_collation(8), collation)


if __name__ == '__main__':
    unittest.main()
