# -*- coding: utf-8 -*-
"""This module defines auto_extract command
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import click
from pathlib2 import Path
from tableausdk.Exceptions import GetLastErrorMessage
from tableausdk.Exceptions import TableauException
from tableausdk.Extract import Extract
from tableausdk.Extract import ExtractAPI

from auto_extract import _status
from auto_extract import _constants
from auto_extract.content_handlers import TDSContentHandler
from auto_extract.exceptions import AutoExtractException
from auto_extract.readers import TDSReader

_RES_STATUS = 'status'
_RES_LOCAL_PATH = 'local-path'
_RES_MSG = 'msg'

_PROGRESS_TEXT = 'Processing datasource files'


@click.command(name='auto_extract')  # noqa: C901
@click.option('-o', '--output-dir', type=click.Path(),
              help='Output directory for generated files')
@click.option('-s', '--suffix', default='',
              help='Adds suffix to generated file names')
@click.option('-p', '--prefix', default='',
              help='Adds prefix to generated file names')
@click.option('--overwrite', is_flag=True,
              help='To overwrite already existing .tde files')
@click.argument('files', nargs=-1, type=click.Path())
def main(files, overwrite, prefix, suffix, output_dir):
    """auto_extract command

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
    absolute_output_dir = None

    if output_dir is not None:
        absolute_output_dir = Path(output_dir).resolve()

    with click.progressbar(files, label=_PROGRESS_TEXT) as file_names:
        for file_name in file_names:
            absolute_path = str(Path(file_name).resolve())

            if absolute_path in tde_success_map:
                continue

            tde_path = _get_tde_path(prefix, file_name, suffix)

            if absolute_output_dir is not None:
                tde_path = absolute_output_dir / tde_path.name

            if overwrite and tde_path.exists():
                tde_path.unlink()

            result = _generate_extract(file_name, str(tde_path))
            tde_success_map[absolute_path] = result

    failed = False
    for key in tde_success_map:
        if tde_success_map[key][_RES_STATUS] == _status.FAILED:
            failed = True
        _print_result(tde_success_map[key], cols=cols)

    ExtractAPI.cleanup()

    if failed:
        raise AutoExtractException(tde_success_map)


def _get_tde_path(prefix, tds_file_name, suffix):
    """Returns tde file path from tds file path

    Parameters
    ----------
    prefix: str
        prefix to add to the filename
    tds_file_name: str
    suffix: str
        suffix to add to the filename

    Returns
    -------
    :py:obj:`~pathlib2.Path`
        path of tde file
    """

    tds_path = Path(tds_file_name)
    tde_file_name = prefix + tds_path.stem + suffix
    tde_path = tds_path.with_name(tde_file_name)
    tde_path = tde_path.with_suffix(_constants.TDE_EXTENSION)

    return tde_path


def _generate_extract(tds_file_name, tde_file_name):
    """Generates a tde file from tds file

    Parameters
    ----------
    tds_file_name : str
        tableau datasource file name / path
    tde_file_name : str
        tableau extract file name / path

    Returns
    -------
    dict
        result in the format

        ::

            {
                'status': True | False depending on success or failure,
                'msg': error message if any,
                'local-path': path of the tableau datasource file
            }
    """

    new_extract = Extract(tde_file_name)
    result = {
        _RES_STATUS: _status.FAILED,
        _RES_LOCAL_PATH: tds_file_name,
        _RES_MSG: ''
    }

    try:
        tds_content_handler = TDSContentHandler()
        tds_reader = TDSReader(tds_content_handler)

        tds_reader.read(tds_file_name)
        table_definition = tds_reader.define_table()

        new_extract.addTable('Extract', tableDefinition=table_definition)

        new_extract.close()
        table_definition.close()

        result[_RES_STATUS] = _status.SUCCESS
    except (IOError, OSError) as err:
        result[_RES_MSG] = str(err)
    except TableauException:
        result[_RES_MSG] = GetLastErrorMessage()

    return result


def _print_result(tde_result, cols=80):
    """Prints result of auto_extract command

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

    file_name = tde_result[_RES_LOCAL_PATH]
    file_status = tde_result[_RES_STATUS]
    message = tde_result[_RES_MSG]

    dots = '.' * (cols - len(file_name) - len(file_status.text) - 1)
    click.echo(file_name + dots, nl=False)
    click.secho(file_status.text, bg=file_status.color)

    if message:
        click.echo(message)


def _compute_cols(files):
    """Computes max required length for output

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
    >>> s = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
    >>> s += 'abcdabcdabcd...Success' + os.linesep
    >>> _compute_cols(files) == len(s)
    True
    """

    if files:
        name_len = max(len(current_file) for current_file in files)
    else:
        name_len = 0

    cols = name_len + 3 + len(_status.SUCCESS.text) + 1
    return max(cols, 80)


if __name__ == '__main__':  # pragma: no cover
    main()  # pylint: disable=locally-disabled,no-value-for-parameter
