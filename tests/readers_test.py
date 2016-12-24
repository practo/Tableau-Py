# -*- coding: utf-8 -*-
"""
Unit Test Cases for readers modules

Classes:

    TestTDSReader

"""
from __future__ import absolute_import

import unittest
import yaml
from auto_extract.content_handlers import TDSContentHandler
from auto_extract.readers import TDSReader


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
        Tests read method

        Assertions:
            * Raises OSError for missing file / directory
            * Raises IOError when file expected but folder or something other
              than file given
            * Raises IOError when file given does not have .tds extension in name

        """
        with self.assertRaisesRegexp(OSError, 'No such file or directory'):
            self.reader.read('sample/random file.tds')

        with self.assertRaisesRegexp(IOError, '^not a file$'):
            self.reader.read('sample')

        with self.assertRaisesRegexp(IOError, '^does not have extension `.tds`$'):
            self.reader.read('tox.ini')

    def test_get_datasource_metadata(self):
        """
        Tests get_datasource_metadata method

        Asserts:
            * Metadata values before calling read
            * Metadata values after calling read

        """

        def test_metadata(metadata, expected_length, expected_value):
            """
            Asserts the correction of metadata value

            Asserts:
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

        test_metadata(self.reader.get_datasource_metadata(), 0, {})

        self.reader.read('sample/sample.tds')

        with open('tests/resources/sample-datasource-metadata-definition.yaml', 'r') as stream:
            expected_result = yaml.load(stream)
            test_metadata(self.reader.get_datasource_metadata(), 2, expected_result)

    def test_get_datasource_column_defs(self):
        """
        Tests get_datasource_column_defs method

        Assertions:
            * Column definition values before calling read
            * Column definition values after calling read

        """

        def test_column_definition(column_definitions, expected_length, expected_value):
            """
            Asserts the correction of column definitions list

            Asserts:
                * Value is not None
                * Value is having expected length
                * Value is instance of list
                * Value is equal to expected value

            """
            self.assertIsNotNone(column_definitions)
            self.assertEqual(len(column_definitions), expected_length)
            self.assertIsInstance(column_definitions, list)
            self.assertListEqual(column_definitions, expected_value)

        test_column_definition(self.reader.get_datasource_column_defs(), 0, [])

        self.reader.read('sample/sample.tds')

        with open('tests/resources/sample-datasource-column-definitions.yaml', 'r') as stream:
            expected_result = yaml.load(stream)
            test_column_definition(self.reader.get_datasource_column_defs(), 9, expected_result)

    def test_define_table(self):
        """
        Tests define_table method

        Assertions:
            * Table Definition value before calling read
            * Table Definition value after calling read
            * Each column in table definition is having the expected name
            * Each column is table definition having the expected type
            * Each column is table definition having expected collation (default collation)

        """
        import re
        import random
        from tableausdk.Extract import TableDefinition
        from tableausdk.Types import Collation, Type

        def test_table_definition(table_def, expected_col_count, expected_collation):
            """
            Asserts the correction of table definition instance

            Asserts:
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

        pattern = re.compile('^_.*')
        collation_types = [x for x in vars(Collation).keys() if not pattern.match(x)]
        collation = getattr(Collation, random.choice(collation_types))

        table_definition = self.reader.define_table(collation=collation)
        test_table_definition(table_definition, 0, collation)

        self.reader.read('sample/sample.tds')

        table_definition = self.reader.define_table(collation=collation)
        test_table_definition(table_definition, 9, collation)

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
