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


if __name__ == '__main__':
    unittest.main()
