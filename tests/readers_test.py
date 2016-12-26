# -*- coding: utf-8 -*-
"""
Unit Test Cases for readers module

Classes:

    TestTDSReader

"""
from __future__ import absolute_import

import unittest
import yaml
from tableausdk.Extract import TableDefinition
from auto_extract.content_handlers import TDSContentHandler
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
        * Raises IOError for missing file / directory
        * Raises IOError when file expected but folder or something other
          than file given
        * Raises IOError when file given does not have .tds extension in name

        """
        with self.assertRaisesRegexp(IOError, 'does not exists'):
            self.reader.read('sample/random file.tds')

        with self.assertRaisesRegexp(IOError, '^not a file$'):
            self.reader.read('sample')

        with self.assertRaisesRegexp(IOError, '^does not have extension `.tds`$'):
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

        self.assertEqual(table_definition.getColumnName(0), '[TABLE_NAME].[LOCAL_COLUMN_NAME1]')
        self.assertEqual(table_definition.getColumnName(1), '[TABLE_NAME].[LOCAL_COLUMN_NAME2]')
        self.assertEqual(table_definition.getColumnName(2), '[TABLE_NAME].[LOCAL_COLUMN_NAME3]')
        self.assertEqual(table_definition.getColumnName(3), '[TABLE_NAME].[LOCAL_COLUMN_NAME4]')
        self.assertEqual(table_definition.getColumnName(4), '[TABLE_NAME].[LOCAL_COLUMN_NAME5]')
        self.assertEqual(table_definition.getColumnName(5), '[TABLE_NAME].[LOCAL_COLUMN_NAME6]')
        self.assertEqual(table_definition.getColumnName(6), '[TABLE_NAME].[LOCAL_COLUMN_NAME7]')
        self.assertEqual(table_definition.getColumnName(7), '[TABLE_NAME].[LOCAL_COLUMN_NAME8]')
        self.assertEqual(table_definition.getColumnName(8), '[TABLE_NAME].[LOCAL_COLUMN_NAME9]')

        self.assertEqual(table_definition.getColumnType(0), Type.DATE)
        self.assertEqual(table_definition.getColumnType(1), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(2), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(3), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(4), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(5), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(6), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(7), Type.CHAR_STRING)
        self.assertEqual(table_definition.getColumnType(8), Type.CHAR_STRING)

        self.assertEqual(table_definition.getColumnCollation(0), collation)
        self.assertEqual(table_definition.getColumnCollation(1), collation)
        self.assertEqual(table_definition.getColumnCollation(2), collation)
        self.assertEqual(table_definition.getColumnCollation(3), collation)
        self.assertEqual(table_definition.getColumnCollation(4), collation)
        self.assertEqual(table_definition.getColumnCollation(5), collation)
        self.assertEqual(table_definition.getColumnCollation(6), collation)
        self.assertEqual(table_definition.getColumnCollation(7), collation)
        self.assertEqual(table_definition.getColumnCollation(8), collation)


if __name__ == '__main__':
    unittest.main()
