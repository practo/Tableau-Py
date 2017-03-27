# -*- coding: utf-8 -*-
"""Unit Test Cases for TDSReader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import yaml

import config
from tableaupy.readers import TDSReader
from tests.readers.base_test import ReaderBaseTest


class TestTDSReader(ReaderBaseTest):
    """Unit Test Cases for testing TDSReader"""

    __test__ = True
    ReaderClass = TDSReader

    def _assert_metadata(self, metadata, expected_length, expected_value):
        """Asserts metadata

        Asserts
        -------
        * value is not None
        * value is having expected length
        * value is instance of dictionary
        * value is equal to expected value
        """

        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), expected_length)
        self.assertIsInstance(metadata, dict)
        self.assertDictEqual(metadata, expected_value)

    def test_extension(self):
        """Tests extension property"""

        self.assertEqual(self.reader.extension, '.tds')

    def test_get_datasource_metadata(self):
        """Tests get_datasource_metadata method

        Asserts
        -------
        * value before calling read
        * value after calling read
        """

        self._assert_metadata(self.reader.get_datasource_metadata(), 0, {})

        self.reader.read(config.SAMPLE_DS_PATH)

        with open(config.TEST_DS_RESULT_METADATA_PATH) as stream:
            expected_result = yaml.load(stream)
            self._assert_metadata(
                self.reader.get_datasource_metadata(),
                2,
                expected_result
            )

    def _assert_column_definitions(
            self,
            column_definitions,
            expected_length,
            expected_value
    ):
        """Asserts column definition

        Asserts
        -------
        * value is not None
        * value is having expected length
        * value is instance of list
        * value is equal to expected value
        """

        self.assertIsNotNone(column_definitions)
        self.assertEqual(len(column_definitions), expected_length)
        self.assertIsInstance(column_definitions, list)
        self.assertListEqual(column_definitions, expected_value)

    def test_get_datasource_column_defs(self):
        """Tests get_datasource_column_defs method

        Asserts
        -------
        * value before calling read
        * value after calling read
        """

        self._assert_column_definitions(
            self.reader.get_datasource_column_defs(),
            0,
            []
        )

        self.reader.read(config.SAMPLE_DS_PATH)

        with open(config.TEST_DS_RESULT_COLUMN_DEFINITION_PATH) as stream:
            expected_result = yaml.load(stream)
            self._assert_column_definitions(
                self.reader.get_datasource_column_defs(),
                9,
                expected_result
            )


if __name__ == '__main__':
    unittest.main()
