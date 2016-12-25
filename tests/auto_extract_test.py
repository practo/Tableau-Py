# -*- coding: utf-8 -*-

"""
Unit Test Cases for auto_extract command

"""
from __future__ import absolute_import

import shutil
import os

from click.testing import CliRunner
from auto_extract.cli import main

RUNNER = CliRunner()
INITIAL_STRING = 'Processing datasource files\n'


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
