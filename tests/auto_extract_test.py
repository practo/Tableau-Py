# -*- coding: utf-8 -*-

"""
Unit Test Cases for auto_extract command

"""
from __future__ import absolute_import

import shutil
import os
import re

from click.testing import CliRunner
from auto_extract.exceptions import AutoExtractException
from auto_extract.cli import main

RUNNER = CliRunner()
INITIAL_STRING = 'Processing datasource files\n'
SUCCESS_PATTERN = re.compile('\\.+Success\n')
FAILED_PATTERN = re.compile('\\.+Failed\n')


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

    def wrapper():
        """Method Wrapper"""
        with open('sample/sample.tds') as sample_stream:
            with RUNNER.isolated_filesystem():
                with open('sample.tds', 'w') as isolated_sample_stream:
                    shutil.copyfileobj(sample_stream, isolated_sample_stream)

                last_modified_time = os.path.getmtime('sample.tds')
                func()
                assert os.path.exists('sample.tds')
                assert os.path.getmtime('sample.tds') == last_modified_time

    return wrapper


@isolated_filesystem
def test_help():
    """
    Asserts:
        * Help works without any error

    """
    result = RUNNER.invoke(main, ['--help'])
    assert result.exit_code == 0


@isolated_filesystem
def test_without_argument():
    """
    Asserts:
        * Command works without any arguments

    """
    result = RUNNER.invoke(main)
    assert result.exit_code == 0
    assert result.output == INITIAL_STRING


@isolated_filesystem
def test_with_single_file():
    """
    Asserts:
        * Progress text is displayed
        * Extract file exists
        * Success is displayed

    """
    result = RUNNER.invoke(main, ['sample.tds'])
    assert result.exit_code == 0
    assert os.path.exists('sample.tde')
    assert result.output.index(INITIAL_STRING) == 0
    assert len(SUCCESS_PATTERN.findall(result.output)) == 1


@isolated_filesystem
def test_with_wrong_filename():
    """
    Asserts:
        * Progress text is displayed
        * OSError is thrown

    """
    result = RUNNER.invoke(main, ['sample1.tds'])
    assert result.exit_code == -1
    assert isinstance(result.exception, OSError)
    assert result.output.index(INITIAL_STRING) == 0


@isolated_filesystem
def test_with_single_file_multiple_times():  # pylint: disable=locally-disabled,invalid-name
    """
    Asserts:
        * Should not throw error when same file is mentioned multiple times
        * Progress text is displayed

    """
    result = RUNNER.invoke(main, ['sample.tds', 'sample.tds'])
    assert result.exit_code == 0
    assert result.output.index(INITIAL_STRING) == 0


@isolated_filesystem
def test_with_multiple_files():
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
    assert result.output.index(INITIAL_STRING) == 0
    assert os.path.exists('sample.tde')
    assert os.path.exists('sample1.tde')
    assert len(SUCCESS_PATTERN.findall(result.output)) == 2
    assert len(FAILED_PATTERN.findall(result.output)) == 0


@isolated_filesystem
def test_with_multiple_calls_without_overwrite():  # pylint: disable=locally-disabled,invalid-name
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
    assert result.output.index(INITIAL_STRING) == 0
    assert len(SUCCESS_PATTERN.findall(result.output)) == 0
    assert len(FAILED_PATTERN.findall(result.output)) == 1
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

>> >> >> > 119
d7a8...Adds
test_with_multiple_calls_without_overwrite
