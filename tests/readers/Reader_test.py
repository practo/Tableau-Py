# -*- coding: utf-8 -*-
"""Unit Test Cases for Reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

from auto_extract.readers import Reader
from auto_extract.readers import ReaderException
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

        """

        expected_regexp = '\'sample/random file.tds\': file does not exists'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            test_filename = os.path.join(config.SAMPLE_PATH, 'random file.tds')
            self.reader.check_file_readable(test_filename)

        expected_regexp = '\'sample\': not a file'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            self.reader.check_file_readable(config.SAMPLE_PATH)

        expected_regexp = '\'tox.ini\': does not have extension `.ext`'
        with self.assertRaisesRegexp(ReaderException, expected_regexp):
            self.reader.check_file_readable('tox.ini')


if __name__ == '__main__':
    unittest.main()
