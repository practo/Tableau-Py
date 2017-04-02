# -*- coding: utf-8 -*-
"""Unit Test Cases for tableaupy command"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import shutil
import unittest

from click.testing import CliRunner
from tableausdk.Extract import Extract
from tableausdk.Extract import TableDefinition
from tableausdk.Types import Collation
from tableausdk.Types import Type

import config
from tableaupy.cli import main
from tableaupy.exceptions import AutoExtractException

RUNNER = CliRunner()


def isolated_filesystem(func):
    """Isolated Filesystem decorator

    Gives isolated filesystem for tableaupy test to run
    thus not polluting the current filesystem

    It copies the current sample/sample.tds to the isolated filesystem

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

    def _assert_text_displayed(self, pattern, result, times):
        self.assertEqual(len(pattern.findall(result.output)), times)

    def _assert_text_not_displayed(self, pattern, result):
        self._assert_text_displayed(pattern, result, 0)

    @isolated_filesystem
    def test_help(self):
        """Tests help option

        Asserts
        -------
        * help works without any error
        * progress text is not displayed
        """

        result = RUNNER.invoke(main, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self._assert_text_not_displayed(self.PROGRESS_TEXT_PATTERN, result)

    @isolated_filesystem
    def test_without_argument(self):
        """Tests without argument

        Asserts
        -------
        * throws SystemExit exception when no argument is given
        * progress text is not displayed
        * error message is displayed indicating files argument is missing
        """

        result = RUNNER.invoke(main)
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(result.output, 'Missing argument "files"')
        self._assert_text_not_displayed(self.PROGRESS_TEXT_PATTERN, result)

    def _assert_table_definition(
            self,
            table_def,
            expected_col_count
    ):
        """asserts table definition

        Asserts
        -------
        * value is not None
        * value is instance of TableDefinition
        * value has expected column count
        """

        self.assertIsNotNone(table_def)
        self.assertIsInstance(table_def, TableDefinition)
        self.assertEqual(table_def.getColumnCount(), expected_col_count)

    @isolated_filesystem
    def test_with_single_file(self):
        """Tests with single file

        Asserts
        -------
        * progress text is displayed
        * extract file exists
        * success is displayed
        * each column in extract is having the expected name
        * each column in extract is having the expected type
        * each column in extract is having the expected collation
        """

        result = RUNNER.invoke(main, ['sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('sample.tde'))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)

        collation = Collation.EN_US_CI
        extract = Extract('sample.tde')
        self.assertTrue(extract.hasTable('Extract'))
        table_definition = extract.openTable('Extract').getTableDefinition()
        self._assert_table_definition(table_definition, 9)

        def col_name(name):
            """makes column name with default table name"""
            return '[{}].[{}]'.format('TABLE_NAME', name)

        get_column_name = table_definition.getColumnName
        get_column_type = table_definition.getColumnType
        get_column_collation = table_definition.getColumnCollation

        self.assertEqual(get_column_name(0), col_name('LOCAL_COLUMN_NAME1'))
        self.assertEqual(get_column_name(1), col_name('LOCAL_COLUMN_NAME2'))
        self.assertEqual(get_column_name(2), col_name('LOCAL_COLUMN_NAME3'))
        self.assertEqual(get_column_name(3), col_name('LOCAL_COLUMN_NAME4'))
        self.assertEqual(get_column_name(4), col_name('LOCAL_COLUMN_NAME5'))
        self.assertEqual(get_column_name(5), col_name('LOCAL_COLUMN_NAME6'))
        self.assertEqual(get_column_name(6), col_name('LOCAL_COLUMN_NAME7'))
        self.assertEqual(get_column_name(7), col_name('LOCAL_COLUMN_NAME8'))
        self.assertEqual(get_column_name(8), col_name('LOCAL_COLUMN_NAME9'))

        self.assertEqual(get_column_type(0), Type.DATE)
        self.assertEqual(get_column_type(1), Type.CHAR_STRING)
        self.assertEqual(get_column_type(2), Type.CHAR_STRING)
        self.assertEqual(get_column_type(3), Type.CHAR_STRING)
        self.assertEqual(get_column_type(4), Type.CHAR_STRING)
        self.assertEqual(get_column_type(5), Type.CHAR_STRING)
        self.assertEqual(get_column_type(6), Type.CHAR_STRING)
        self.assertEqual(get_column_type(7), Type.CHAR_STRING)
        self.assertEqual(get_column_type(8), Type.CHAR_STRING)

        self.assertEqual(get_column_collation(0), 0)
        self.assertEqual(get_column_collation(1), collation)
        self.assertEqual(get_column_collation(2), collation)
        self.assertEqual(get_column_collation(3), collation)
        self.assertEqual(get_column_collation(4), collation)
        self.assertEqual(get_column_collation(5), collation)
        self.assertEqual(get_column_collation(6), collation)
        self.assertEqual(get_column_collation(7), collation)
        self.assertEqual(get_column_collation(8), collation)

    @isolated_filesystem
    def test_with_wrong_filename(self):
        """Tests with wrong filename

        Asserts
        -------
        * progress text is not displayed
        * systemExit error is thrown
        * exit code should be 2
        * file is not created
        """

        result = RUNNER.invoke(main, ['sample1.tds'])
        self.assertEqual(result.exit_code, 2)
        self.assertIsInstance(result.exception, SystemExit)
        self._assert_text_not_displayed(self.PROGRESS_TEXT_PATTERN, result)
        self.assertFalse(os.path.exists('sample1.tde'))

    @isolated_filesystem
    def test_with_single_file_multiple_times(self):
        """Tests with single file passed as multiple params

        Asserts
        -------
        * throws error when same file is mentioned multiple times
        * progress text is displayed
        """

        result = RUNNER.invoke(main, ['sample.tds', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)

    @isolated_filesystem
    def test_with_multiple_files(self):
        """Tests with multiple files as argument

        Asserts
        -------
        * 2 different files can be invoked at the sample time
        * progress text is displayed
        * 2 files are generated
        * success if returned for both the files
        * failed is not printed
        """

        shutil.copy('sample.tds', 'sample1.tds')
        result = RUNNER.invoke(main, ['sample.tds', 'sample1.tds'])
        self.assertEqual(result.exit_code, 0)
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self.assertTrue(os.path.exists('sample.tde'))
        self.assertTrue(os.path.exists('sample1.tde'))
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 2)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

    @isolated_filesystem
    def test_with_multiple_calls_without_overwrite(self):
        """Tests with multiple calls on a file without overwrite option

        Asserts
        -------
        * if tde already exists with same table name give error
        * progress text is displayed
        * error Message and Failed object
        * failed is printed
        * success is not printed

        TODO
        ----
        * Overwrite with duplicate table name and without
        """

        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tds'])
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, AutoExtractException)
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_not_displayed(self.SUCCESS_PATTERN, result)
        self._assert_text_displayed(self.FAILED_PATTERN, result, 1)
        result_values = result.exc_info[1].args[0].values()
        self.assertEqual(len(result_values), 1)
        self.assertIsNotNone(result_values[0].get('status'))
        self.assertEqual(result_values[0].get('status'), {
            'color': 'red',
            'text': 'Failed'
        })
        self.assertIsNotNone(result_values[0].get('local-path'))
        self.assertEqual(result_values[0].get('local-path'), 'sample.tds')
        self.assertIsNotNone(result_values[0].get('msg'))
        message = '\'.*/sample.tde\': file already exists'
        self.assertRegexpMatches(result_values[0].get('msg'), message)

    @isolated_filesystem
    def test_with_overwrite(self):
        """Tests with multiple calls on a file with overwrite option

        Asserts
        -------
        * overwrite option works
        * progress is displayed
        * file is generated
        * success is printed both the times
        * failed is not printed both times
        """

        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        self.assertEqual(result.exit_code, 0)
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

        result = RUNNER.invoke(main, ['sample.tds', '--overwrite'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('sample.tde'))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

    @isolated_filesystem
    def test_with_any_other_extension(self):
        """Tests with filename having non *.tds extension

        Asserts
        -------
        * gives error with any other extension file
        * progress text is displayed
        * throws errors and the error message
        * success is not printed
        * failed is printed once
        """

        RUNNER.invoke(main, ['sample.tds'])
        result = RUNNER.invoke(main, ['sample.tde'])
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, AutoExtractException)
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.FAILED_PATTERN, result, 1)
        self._assert_text_not_displayed(self.SUCCESS_PATTERN, result)
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
        * runs successfully when suffix option is given
        * progress text is displayed
        * success is printed
        * failed is not printed
        * generated file with suffix exists
        """

        result = RUNNER.invoke(main, ['--suffix', '_TDE', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('sample_TDE.tde'))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

    @isolated_filesystem
    def test_with_prefix(self):
        """Tests with prefix option

        Asserts
        -------
        * runs successfully when prefix option is given
        * progress text is displayed
        * success is printed
        * failed is not printed
        * generated file with prefix exists
        """

        result = RUNNER.invoke(main, ['--prefix', 'TDE_', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('TDE_sample.tde'))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

    @isolated_filesystem
    def test_with_prefix_and_suffix(self):
        """Tests with both prefix and suffix option

        Asserts
        -------
        * runs successfully when prefix and suffix option is given
        * progress text is displayed
        * success is printed
        * failed is not printed
        * generated file with prefix and suffix exists
        """

        result = RUNNER.invoke(main, [
            '--prefix',
            'TDE_',
            '--suffix',
            '_TDE',
            'sample.tds',
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists('TDE_sample_TDE.tde'))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)

    @isolated_filesystem
    def test_with_output_dir_when_not_exist(self):
        """Tests with output dir option when it doesn't exists

        Asserts
        -------
        * completes unsuccessfully with SystemExit
        * file is not created
        * progress bar is not displayed
        """

        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        self.assertEqual(result.exit_code, 2)
        self._assert_text_not_displayed(self.PROGRESS_TEXT_PATTERN, result)
        self.assertFalse(os.path.exists(os.path.join('temp', 'sample.tde')))
        self.assertIsInstance(result.exception, SystemExit)

    @isolated_filesystem
    def test_with_output_dir_when_exist(self):
        """Tests with output dir option when it exists

        Asserts
        -------
        * completes successfully
        * progress text is displayed
        * success is printed
        * failed is not printed
        * generated file is saved in temporary folder
        """

        os.mkdir('temp')
        result = RUNNER.invoke(main, ['--output-dir', 'temp', 'sample.tds'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(os.path.join('temp', 'sample.tde')))
        self._assert_text_displayed(self.PROGRESS_TEXT_PATTERN, result, 1)
        self._assert_text_displayed(self.SUCCESS_PATTERN, result, 1)
        self._assert_text_not_displayed(self.FAILED_PATTERN, result)
