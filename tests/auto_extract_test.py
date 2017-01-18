# -*- coding: utf-8 -*-

"""
Unit Test Cases for auto_extract command

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import shutil
import unittest

from click.testing import CliRunner

from auto_extract.cli import main
from auto_extract.exceptions import AutoExtractException
import config

RUNNER = CliRunner()


def isolated_filesystem(func):
    """Isolated Filesystem decorator

    Gives isolated filesystem for auto_extract test to run
    thus not polluting the current filesystem

    It copies the current sample/sample.tds to the isolated filesystem

    Parameters
    ----------
    func : test_case to run

    Returns
    -------
    wrapper around the test case to run it in isolated filesystem

    Asserts
    -------
    * Original tableau datasource file is not deleted
    * Original tableau datasource file is not modified
    """

    def wrapper(*args, **kwargs):
        """Method Wrapper"""
        with open(config.SAMPLE_DS_PATH) as sample_stream:
            with RUNNER.isolated_filesystem():
                with open('sample.tds', 'w') as isolated_sample_stream:
                    shutil.copyfileobj(sample_stream, isolated_sample_stream)

                last_modified_time = os.path.getmtime('sample.tds')
                func(*args, **kwargs)
                assert os.path.exists('sample.tds')
                assert os.path.getmtime('sample.tds') == last_modified_time

    return wrapper


class TestAutoExtractCommand(unittest.TestCase):
    """Unit Test Cases for auto_extract command

    DATA
    ----
    PROGRESS_TEXT_PATTERN : re
        tests the presence progress text
    SUCCESS_PATTERN : re
        tests the presence of Success in output
    FAILED_PATTERN : re
        tests the presence of Failed in output
    """

    PROGRESS_TEXT_PATTERN = re.compile('^Processing datasource files\n')
    SUCCESS_PATTERN = re.compile('\\.+Success\n')
    FAILED_PATTERN = re.compile('\\.+Failed\n')

    @isolated_filesystem
    def test_help(self):
        """Tests help option

        Asserts
        -------
        * Help works without any error
        * Progress text is not displayed
        """

        result = RUNNER.invoke(main, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_without_argument(self):
        """Tests without argument

        Asserts
        -------
        * Command works without any arguments
        * Progress text is displayed
        """

        result = RUNNER.invoke(main)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)

    @isolated_filesystem
    def test_with_single_file(self):
        """Tests with single file

        Asserts
        -------
        * Progress text is displayed
        * Extract file exists
        * Success is displayed
        """

        result = RUNNER.invoke(main, ['sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('sample.tde'))
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)

    @isolated_filesystem
    def test_with_wrong_filename(self):
        """Tests with wrong filename

        Asserts
        -------
        * Progress text is displayed
        * OSError is thrown
        """

        result = RUNNER.invoke(main, ['sample1.tds'])
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, OSError)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)

    @isolated_filesystem
    def test_with_single_file_multiple_times(self):  # pylint: disable=locally-disabled,invalid-name
        """Tests with single file passed as multiple params

        Asserts
        -------
        * Should not throw error when same file is mentioned multiple times
        * Progress text is displayed
        """

        result = RUNNER.invoke(main, ['sample.tds', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)

    @isolated_filesystem
    def test_with_multiple_files(self):
        """Tests with multiple files as argument

        Asserts
        -------
        * 2 different files can be invoked at the sample time
        * Progress text is displayed
        * 2 files are generated
        * Success if returned for both the files
        * Failed is not printed
        """

        shutil.copy('sample.tds', 'sample1.tds')
        result = RUNNER.invoke(main, ['sample.tds', 'sample1.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists('sample.tde'))
        self.assertTrue(os.path.exists('sample1.tde'))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 2)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_with_multiple_calls_without_overwrite(self):  # pylint: disable=locally-disabled,invalid-name
        """Tests with multiple calls on a file without overwrite option

        Asserts
        -------
        * If tde already exists with same table name give error
        * Progress text is displayed
        * Error Message and Failed object
        * Failed is printed
        * Success is not printed
        """

        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tds'])
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, AutoExtractException)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 0)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 1)
        self.assertEqual(result.exc_info[1].args[0].values(), [
            {
                'status': {
                    'color': 'red',
                    'text': 'Failed'
                },
                'local-path': 'sample.tds',
                'msg': 'duplicate table name'
            }
        ])

    @isolated_filesystem
    def test_with_overwrite(self):
        """Tests with multiple calls on a file with overwrite option

        Asserts
        -------
        * Overwrite option works
        * Progress is displayed
        * File is generated
        * Success is printed both the times
        * Failed is not printed both times
        """

        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists('sample.tde'))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_with_any_other_extension(self):
        """Tests with filename having non *.tds extension

        Asserts
        -------
        * Gives error with any other extension file
        * Progress text is displayed
        * Throws errors and the error message
        * Success is not printed
        * 1 Failed is printed
        """

        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tde'])
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertIsInstance(result.exception, AutoExtractException)
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 0)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 1)
        self.assertEqual(result.exc_info[1].args[0].values(), [
            {
                'status': {
                    'color': 'red',
                    'text': 'Failed'
                },
                'local-path': 'sample.tde',
                'msg': '\'sample.tde\': does not have extension `.tds`'
            }
        ])

    @isolated_filesystem
    def test_with_suffix(self):
        """Tests with suffix option

        Asserts
        -------
        * Runs successfully when suffix option is given
        * Progress text is displayed
        * Success is printed
        * Failed is not printed
        * Generated file with suffix exists
        """

        result = RUNNER.invoke(main, ['--suffix', '_TDE', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists('sample_TDE.tde'))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_with_prefix(self):
        """Tests with prefix option

        Asserts
        -------
        * Runs successfully when prefix option is given
        * Progress text is displayed
        * Success is printed
        * Failed is not printed
        * Generated file with prefix exists
        """

        result = RUNNER.invoke(main, ['--prefix', 'TDE_', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists('TDE_sample.tde'))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_with_prefix_and_suffix(self):
        """Tests with both prefix and suffix option

        Asserts
        -------
        * Runs successfully when prefix and suffix option is given
        * Progress text is displayed
        * Success is printed
        * Failed is not printed
        * Generated file with prefix and suffix exists
        """

        result = RUNNER.invoke(main, ['--prefix', 'TDE_', '--suffix', '_TDE', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists('TDE_sample_TDE.tde'))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)

    @isolated_filesystem
    def test_with_output_dir_when_not_exist(self):  # pylint: disable=locally-disabled,invalid-name
        """Tests with output dir option when it doesn't exists

        Asserts
        -------
        * completes unsuccessfully with OSError
        * File is not created
        """

        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 0)
        self.assertFalse(os.path.exists(os.path.join('temp', 'sample.tde')))
        self.assertIsInstance(result.exception, OSError)

    @isolated_filesystem
    def test_with_output_dir_when_exist(self):
        """Tests with output dir option when it exists

        Asserts
        -------
        * completes successfully
        * Progress text is displayed
        * Success is printed
        * Failed is not printed
        * Generated file is saved in temporary folder
        """

        os.mkdir('temp')
        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(self.PROGRESS_TEXT_PATTERN.findall(result.output)), 1)
        self.assertTrue(os.path.exists(os.path.join('temp', 'sample.tde')))
        self.assertEqual(len(self.SUCCESS_PATTERN.findall(result.output)), 1)
        self.assertEqual(len(self.FAILED_PATTERN.findall(result.output)), 0)
