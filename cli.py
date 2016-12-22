# -*- coding: utf-8 -*-
"""
This module defines auto_extract command

"""
from __future__ import absolute_import, print_function

from tableausdk.Exceptions import TableauException, GetLastErrorMessage
from tableausdk.Extract import ExtractAPI, Extract

from pathlib2 import Path

from auto_extract.content_handlers import TDSContentHandler
from auto_extract.readers import TDSReader
from auto_extract import _status
import click


@click.command(name='auto_extract')
@click.option('--overwrite', is_flag=True, help='To overwrite already existing .tde files')
@click.argument('files', nargs=-1, type=click.Path())
def main(files, overwrite):
    """
    The script creates tableau datasource extracts corresponding
    to input tableau datasource `FILES`.

    If a .tde file already exists, --overwrite option will overwrite that
    .tde file or else processing of corresponding tableau datasource will
    fail with proper error message.

    `FILES` include list of filenames / filepaths and it accepts characters
    like '*', anything that will result in a valid file path.

    OSError will be raised otherwise.

    """
    ExtractAPI.initialize()
    tde_success_map = dict()

    cols = _compute_cols(files)

    with click.progressbar(files, label='Processing datasource files') as file_names:
        for file_name in file_names:
            absolute_path = str(Path(file_name).resolve())

            if absolute_path in tde_success_map:
                continue

            table_definition = None
            tde_path = Path(file_name).with_suffix('.tde')

            tde_success_map[absolute_path] = {
                'status': _status.FAILED,
                'local-path': file_name,
                'msg': ''
            }

            if overwrite and tde_path.exists():
                tde_path.unlink()

            new_extract = Extract(str(tde_path))

            try:
                tds_content_handler = TDSContentHandler()
                tds_reader = TDSReader(tds_content_handler)

                tds_reader.read(file_name)
                table_definition = tds_reader.define_table()

                new_extract.addTable('Extract', tableDefinition=table_definition)
                tde_success_map[absolute_path]['status'] = _status.SUCCESS
            except (IOError, OSError) as err:
                tde_success_map[absolute_path]['msg'] = str(err)
            except TableauException:
                tde_success_map[absolute_path]['msg'] = GetLastErrorMessage()
            finally:
                if table_definition is not None:
                    table_definition.close()

                # Close the extract in order to save the .tde file and clean up resources
                new_extract.close()

    for key in tde_success_map:
        _print_result(tde_success_map[key], cols=cols)

    ExtractAPI.cleanup()


def _print_result(tde_result, cols=80):
    """

    Parameters
    ----------
    tde_result : dict
        Represented in form::

            {
                'local-path': File path (not absolute),
                'status': Passed | Failed
                'msg': error_message || ''
            }
    cols : int
        Length of a line in the print result. The value is,
        calculated by taking into account the names of all files,
        and maximum length of status to accommodate everything in a neat
        tabular form. Defaults to 80.

    """
    file_name = tde_result['local-path']
    file_status = tde_result['status']
    message = tde_result['msg']

    dots = '.' * (cols - len(file_name) - len(file_status.get('text')) - 1)
    click.echo(file_name + dots, nl=False)
    click.secho(file_status.get('text'), bg=file_status.get('color'))

    if message:
        click.echo(message)


def _compute_cols(files):
    """
    From all the file names and maximum length of _status constant text,
    determines the maximum length a line can have in the result.

    Parameters
    ----------
    files : list
        list of all the files input by the user.

    Returns
    -------
    int
        maximum line length of output result, min: 80

    Examples
    --------
    >>> files = ['abcd', 'abcde', 'abcdf']
    >>> _compute_cols(files)
    80

    >>> import os
    >>> files = ['abcd', 'abcd'*18]
    >>> s = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd...Success'
    >>> s += os.linesep
    >>> _compute_cols(files) == len(s)
    True

    """
    if files:
        name_len = max(len(current_file) for current_file in files)
    else:
        name_len = 0

    cols = name_len + 3 + len(_status.SUCCESS['text']) + 1
    return max(cols, 80)


if __name__ == '__main__':
    main()  # pylint: disable=locally-disabled,no-value-for-parameter
