# -*- coding: utf-8 -*-
"""Unit Test Cases for TDSReader"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

import yaml

from tableaupy.contenthandlers import TDSContentHandler
from tableaupy.readers import exceptions
from tableaupy.readers import TDSReader
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
        * For each assertions above:
            - checks original exception type
            - checks if their cause is None
            - checks if the arguments are correctly populated
            - checks if the error attributes are correctly set

        TODO
        ----
        * To check when the xml parsing of file fails ReaderException is thrown
        * To check when the ContentHandler fails to parse, ReaderException is thrown

        """
        file_path = os.path.join(config.SAMPLE_PATH, 'random file.tds')
        regex = '\'{}\': file does not exists'.format(file_path)
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.read(file_path)

        self.assertIsInstance(err.exception, exceptions.FileNotFound)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path,))
        self.assertEqual(err.exception.file, file_path)

        file_path = config.SAMPLE_PATH
        regex = '\'{}\': not a file'.format(file_path)
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.read(file_path)

        self.assertIsInstance(err.exception, exceptions.NodeNotFile)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path,))
        self.assertEqual(err.exception.file, file_path)

        file_path = 'tox.ini'
        regex = '\'{}\': does not have extension `.tds`'.format(file_path)
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.read(file_path)

        self.assertIsInstance(err.exception, exceptions.FileExtensionMismatch)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path, '.tds'))
        self.assertEqual(err.exception.file, file_path)
        self.assertEqual(err.exception.extension, '.tds')

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
