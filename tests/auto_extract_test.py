# -*- coding: utf-8 -*-

"""
Unit Test Cases for auto_extract command

"""
from __future__ import absolute_import

import shutil
import os
import re
import unittest

from click.testing import CliRunner
from auto_extract.exceptions import AutoExtractException
from auto_extract.cli import main

RUNNER = CliRunner()


def isolated_filesystem(func):
    """
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
        with open('sample/sample.tds') as sample_stream:
            with RUNNER.isolated_filesystem():
                with open('sample.tds', 'w') as isolated_sample_stream:
                    shutil.copyfileobj(sample_stream, isolated_sample_stream)

                last_modified_time = os.path.getmtime('sample.tds')
                func(*args, **kwargs)
                assert os.path.exists('sample.tds')
                assert os.path.getmtime('sample.tds') == last_modified_time

    return wrapper


class TestAutoExtractCommand(unittest.TestCase):
    """
    Unit Test Cases for auto_extract command

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
        """
        Asserts:
            * Help works without any error
            * Progress text is not displayed

        """
        result = RUNNER.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 0

    @isolated_filesystem
    def test_without_argument(self):
        """
        Asserts:
            * Command works without any arguments
            * Progress text is displayed

        """
        result = RUNNER.invoke(main)
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1

    @isolated_filesystem
    def test_with_single_file(self):
        """
        Asserts:
            * Progress text is displayed
            * Extract file exists
            * Success is displayed

        """
        result = RUNNER.invoke(main, ['sample.tds'])
        assert result.exit_code == 0
        assert os.path.exists('sample.tde')
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1

    @isolated_filesystem
    def test_with_wrong_filename(self):
        """
        Asserts:
            * Progress text is displayed
            * OSError is thrown

        """
        result = RUNNER.invoke(main, ['sample1.tds'])
        assert result.exit_code == -1
        assert isinstance(result.exception, OSError)
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1

    @isolated_filesystem
    def test_with_single_file_multiple_times(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * Should not throw error when same file is mentioned multiple times
            * Progress text is displayed

        """
        result = RUNNER.invoke(main, ['sample.tds', 'sample.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1

    @isolated_filesystem
    def test_with_multiple_files(self):
        """
        Asserts:
            * 2 different files can be invoked at the sample time
            * Progress text is displayed
            * 2 files are generated
            * Success if returned for both the files
            * Failed is not printed

        """
        shutil.copy('sample.tds', 'sample1.tds')
        result = RUNNER.invoke(main, ['sample.tds', 'sample1.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert os.path.exists('sample.tde')
        assert os.path.exists('sample1.tde')
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 2
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0

    @isolated_filesystem
    def test_with_multiple_calls_without_overwrite(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * If tde already exists with same table name give error
            * Progress text is displayed
            * Error Message and Failed object
            * Failed is printed
            * Success is not printed

        """
        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tds'])
        assert result.exit_code == -1
        assert isinstance(result.exception, AutoExtractException)
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 0
        assert len(self.FAILED_PATTERN.findall(result.output)) == 1
        assert result.exc_info[1].args[0].values() == [
            {
                'status': {
                    'color': 'red',
                    'text': 'Failed'
                },
                'local-path': 'sample.tds',
                'msg': 'duplicate table name'
            }
        ]

    @isolated_filesystem
    def test_with_overwrite(self):
        """
        Asserts:
            * Overwrite option works
            * Progress is displayed
            * File is generated
            * Success is printed both the times
            * Failed is not printed both times

        """
        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0

        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert os.path.exists('sample.tde')
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0

    @isolated_filesystem
    def test_with_any_other_extension(self):
        """
        Asserts:
            * Gives error with any other extension file
            * Progress text is displayed
            * Throws errors and the error message
            * Success is not printed
            * 1 Failed is printed

        """
        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tde'])
        assert result.exit_code == -1
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert isinstance(result.exception, AutoExtractException)
        assert len(self.FAILED_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 0
        assert result.exc_info[1].args[0].values() == [
            {
                'status': {
                    'color': 'red',
                    'text': 'Failed'
                },
                'local-path': 'sample.tde',
                'msg': 'does not have extension `.tds`'
            }
        ]

    @isolated_filesystem
    def test_with_suffix(self):
        """
        Asserts:
            * Runs successfully when suffix option is given
            * Progress text is displayed
            * Success is printed
            * Failed is not printed
            * Generated file with suffix exists

        """
        result = RUNNER.invoke(main, ['--suffix', '_TDE', 'sample.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0
        assert os.path.exists('sample_TDE.tde')

    @isolated_filesystem
    def test_with_prefix(self):
        """
        Asserts:
            * Runs successfully when prefix option is given
            * Progress text is displayed
            * Success is printed
            * Failed is not printed
            * Generated file with prefix exists

        """
        result = RUNNER.invoke(main, ['--prefix', 'TDE_', 'sample.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0
        assert os.path.exists('TDE_sample.tde')

    @isolated_filesystem
    def test_with_prefix_and_suffix(self):
        """
        Asserts:
            * Runs successfully when prefix and suffix option is given
            * Progress text is displayed
            * Success is printed
            * Failed is not printed
            * Generated file with prefix and suffix exists

        """
        result = RUNNER.invoke(main, ['--prefix', 'TDE_', '--suffix', '_TDE', 'sample.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0
        assert os.path.exists('TDE_sample_TDE.tde')

    @isolated_filesystem
    def test_with_output_dir_when_not_exist(self):  # pylint: disable=locally-disabled,invalid-name
        """
        Asserts:
            * completes unsuccessfully with OSError
            * File is not created

        """
        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        assert result.exit_code == -1
        assert not os.path.exists(os.path.join('temp', 'sample.tde'))
        assert isinstance(result.exception, OSError)
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 0

    @isolated_filesystem
    def test_with_output_dir_when_exist(self):
        """
        Asserts:
            * completes successfully
            * Progress text is displayed
            * Success is printed
            * Failed is not printed
            * Generated file is saved in temporary folder

        """
        os.mkdir('temp')
        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        assert result.exit_code == 0
        assert len(self.PROGRESS_TEXT_PATTERN.findall(result.output)) == 1
        assert len(self.SUCCESS_PATTERN.findall(result.output)) == 1
        assert len(self.FAILED_PATTERN.findall(result.output)) == 0
        assert os.path.exists(os.path.join('temp', 'sample.tde'))
