# -*- coding: utf-8 -*-
"""Unit Test Cases for Reader base class"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

import config
from tableaupy.readers import exceptions


class ReaderBaseTest(unittest.TestCase):
    """Unit Test Cases for Reader

    Since the __test__ property is False this is not going to be run as a test
    case. Also pylint rule not-callable is disabled in setUp because by default
    ReaderClass is None.

    It is expected that test cases having this test class as parent will be
    having __test__ = True and ReaderClass assigned to a ReaderClass for setUp
    to instantiate a reader object.
    """

    __test__ = False
    maxDiff = True
    ReaderClass = None

    def setUp(self):
        self.reader = self.ReaderClass()  # pylint: disable=not-callable

    def tearDown(self):
        self.reader = None

    def test_read(self):
        """Tests read method

        Asserts
        -------
        * raises ReaderException for missing file / directory
        * raises ReaderException when file expected but folder or
          something other than file given
        * raises ReaderException when file does not have correct extension
        * for each assertions above:
            - checks original exception type
            - checks if their cause is None
            - checks if the arguments are correctly populated
            - checks if the error attributes are correctly set

        TODO
        ----
        * check when the xml parsing of file fails ReaderException is thrown
        * check when ContentHandler fails to parse, ReaderException is thrown
        """

        extension = self.reader.extension
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
        regex = '\'{}\': does not have extension `{}`'.format(
            file_path, extension
        )
        with self.assertRaisesRegexp(exceptions.ReaderException, regex) as err:
            self.reader.read(file_path)

        self.assertIsInstance(err.exception, exceptions.FileExtensionMismatch)
        self.assertIsNone(err.exception.cause)
        self.assertEqual(err.exception.args, (file_path, extension))
        self.assertEqual(err.exception.file, file_path)
        self.assertEqual(err.exception.extension, extension)


if __name__ == '__main__':
    unittest.main()
