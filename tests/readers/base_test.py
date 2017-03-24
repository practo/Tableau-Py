# -*- coding: utf-8 -*-
"""Unit Test Cases for Reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

from tableaupy.readers import exceptions
from tableaupy.readers import Reader

import config


class TestReader(unittest.TestCase):
    """Unit Test Cases for Reader"""

    EXTENSION = '.ext'

    def setUp(self):
        self.reader = Reader(self.EXTENSION)

    def tearDown(self):
        self.reader = None

    def test_check_file_readable(self):
        """Tests check_file_readable method

        Asserts
        -------
        * Raises ReaderException for missing file / directory
        * Raises ReaderException when file expected but folder or
          something other than file given
        * Raises ReaderException when file given does not have .tds extension in name
        * For each assertions above:
            - checks original exception type
            - checks if their cause is None
            - checks if the arguments are correctly populated
            - checks if the error attributes are correctly set
        """

        file_path = os.path.join(config.SAMPLE_PATH, 'random file.tds')
        regex = '\'{}\': file does not exists'.format(file_path)

        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.check_file_readable(file_path)

        self.assertIsInstance(err.exception, exceptions.FileNotFound)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path,))
        self.assertEqual(err.exception.file, file_path)

        file_path = config.SAMPLE_PATH
        regex = '\'{}\': not a file'.format(file_path)
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.check_file_readable(file_path)

        self.assertIsInstance(err.exception, exceptions.NodeNotFile)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path,))
        self.assertEqual(err.exception.file, file_path)

        file_path = 'tox.ini'
        regex = '\'{}\': does not have extension `{}`'.format(
            file_path, self.EXTENSION
        )
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.check_file_readable(file_path)

        self.assertIsInstance(err.exception, exceptions.FileExtensionMismatch)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path, self.EXTENSION))
        self.assertEqual(err.exception.file, file_path)
        self.assertEqual(err.exception.extension, self.EXTENSION)


if __name__ == '__main__':
    unittest.main()
