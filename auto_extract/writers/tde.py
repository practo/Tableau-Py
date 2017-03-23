# -*- coding: utf-8 -*-
"""This module defines extract writer"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from future.utils import raise_with_traceback
from tableausdk.Exceptions import GetLastErrorMessage
from tableausdk.Exceptions import TableauException
from tableausdk.Extract import Extract
from tableausdk.Extract import ExtractAPI
from tableausdk.Extract import TableDefinition
from tableausdk.Types import Collation
from tableausdk.Types import Type

from auto_extract.contenthandlers import TDSContentHandler
from auto_extract.exceptions import UnexpectedNoneValue
from auto_extract.readers import ReaderException
from auto_extract.readers import TDSReader
from auto_extract.writers.exceptions import WriterException
from auto_extract.writers.base import Writer


class TDEWriter(Writer):
    """Writer class for Tableau extract files (\\*.tde)"""

    _collation_map = {
        'ar': Collation.AR,
        'binary': Collation.BINARY,
        'cs': Collation.CS,
        'cs_ci': Collation.CS_CI,
        'cs_ci_ai': Collation.CS_CI_AI,
        'da': Collation.DA,
        'de': Collation.DE,
        'el': Collation.EL,
        'en_gb': Collation.EN_GB,
        'en_us': Collation.EN_US,
        'en_us_ci': Collation.EN_US_CI,
        'es': Collation.ES,
        'es_ci_ai': Collation.ES_CI_AI,
        'et': Collation.ET,
        'fi': Collation.FI,
        'fr_ca': Collation.FR_CA,
        'fr_fr': Collation.FR_FR,
        'fr_fr_ci_ai': Collation.FR_FR_CI_AI,
        'he': Collation.HE,
        'hu': Collation.HU,
        'is': Collation.IS,
        'it': Collation.IT,
        'ja': Collation.JA,
        'ja_jis': Collation.JA_JIS,
        'ko': Collation.KO,
        'lt': Collation.LT,
        'lv': Collation.LV,
        'nl_nl': Collation.NL_NL,
        'nn': Collation.NN,
        'pl': Collation.PL,
        'pt_br': Collation.PT_BR,
        'pt_br_ci_ai': Collation.PT_BR_CI_AI,
        'pt_pt': Collation.PT_PT,
        'root': Collation.ROOT,
        'ru': Collation.RU,
        'sl': Collation.SL,
        'sv_fi': Collation.SV_FI,
        'sv_se': Collation.SV_SE,
        'tr': Collation.TR,
        'uk': Collation.UK,
        'vi': Collation.VI,
        'zh_hans_cn': Collation.ZH_HANS_CN,
        'zh_hant_tw': Collation.ZH_HANT_TW,
    }

    _type_map = {
        'boolean': Type.BOOLEAN,
        'string': Type.CHAR_STRING,
        'date': Type.DATE,
        'datetime': Type.DATETIME,
        'integer': Type.INTEGER,
        'double': Type.DOUBLE,
        'duration': Type.DURATION,
        'unicode_string': Type.UNICODE_STRING,
    }

    def __init__(self, options=None):
        super(TDEWriter, self).__init__('.tde', options)
        ExtractAPI.initialize()

    def __del__(self):
        ExtractAPI.cleanup()

    def _define_table(self, tds_reader, collation):
        """Returns TableDefinition object from parsed metadata-records

        The method uses Tableau Extract module to create Table Definition
        object from parsed column information.

        Parameters
        ----------
        tds_reader: TDSReader
            containing parsed information from a tableau datasource file
        collation: Collation
            collation to be used for all columns of the table

        Returns
        -------
        TableDefinition
            tableau definition object from parsed tableau datasource file

        Note
        ----
        If the column type information is not available, it will use default
        column type as Type.UNICODE_STRING

        Raises
        ------
        TableauException
            when Tableau SDK fails to add column in table definition
        WriterException
            * when parent_name is None in column_definition
            * when local_name is None in column_definition
            * when a KeyError is occurred while fetching data
        """

        table_definition = TableDefinition()
        column_definitions = tds_reader.get_datasource_column_defs()

        table_definition.setDefaultCollation(collation)

        for i, col_def in enumerate(column_definitions, start=1):
            try:
                [parent_name, local_name, local_type] = [
                    col_def.get(TDSContentHandler.K_COL_DEF_PARENT_NAME),
                    col_def.get(TDSContentHandler.K_COL_DEF_LOCAL_NAME),
                    col_def.get(TDSContentHandler.K_COL_DEF_LOCAL_TYPE),
                ]

                if parent_name is None:
                    raise UnexpectedNoneValue(
                        TDSContentHandler.K_COL_DEF_PARENT_NAME
                    )

                if local_name is None:
                    raise UnexpectedNoneValue(
                        TDSContentHandler.K_COL_DEF_LOCAL_NAME
                    )

                column_name = '{}.{}'.format(parent_name, local_name)
                column_type = self._type_map.get(
                    local_type,
                    self._type_map['unicode_string']
                )

                table_definition.addColumn(column_name, column_type)
            except (UnexpectedNoneValue, KeyError) as err:
                err.args += (i, col_def)
                raise_with_traceback(WriterException(err))

        return table_definition

    def generate_from_tds(self,
                          tds_file_name,
                          collation='en_us_ci'):
        """Generates a tableau extract file from tableau datasource file

        Default behaviour is to place the files in the same folder as the tds
        files unless output_dir is specified

        Parameters
        ----------
        tds_file_name: str
            tableau datasource file name / path
        collation: str
            default column collation (default: "en_us_ci")

        Raises
        ------
        WriterException
            when not able to read/write datasource/extract file
            when not able to process tableau data table

        Note
        ----
        Following are considered valid collation values:

        * ar          - Internal binary representation
        * binary      - Arabic
        * cs          - Czech
        * cs_ci       - Czech (Case Insensitive)
        * cs_ci_ai    - Czech (Case/Accent Insensitive
        * da          - Danish
        * de          - German
        * el          - Greek
        * en_gb       - English (Great Britain)
        * en_us       - English (US)
        * en_us_ci    - English (US, Case Insensitive)
        * es          - Spanish
        * es_ci_ai    - Spanish (Case/Accent Insensitive)
        * et          - Estonian
        * fi          - Finnish
        * fr_ca       - French (Canada)
        * fr_fr       - French (France)
        * fr_fr_ci_ai - French (France, Case/Accent Insensitive)
        * he          - Hebrew
        * hu          - Hungarian
        * is          - Icelandic
        * it          - Italian
        * ja          - Japanese
        * ja_jis      - Japanese (JIS)
        * ko          - Korean
        * lt          - Lithuanian
        * lv          - Latvian
        * nl_nl       - Dutch (Netherlands)
        * nn          - Norwegian
        * pl          - Polish
        * pt_br       - Portuguese (Brazil)
        * pt_br_ci_ai - Portuguese (Brazil Case/Accent Insensitive)
        * pt_pt       - Portuguese (Portugal)
        * root        - Root
        * ru          - Russian
        * sl          - Slovenian
        * sv_fi       - Swedish (Finland)
        * sv_se       - Swedish (Sweden)
        * tr          - Turkish
        * uk          - Ukrainian
        * vi          - Vietnamese
        * zh_hans_cn  - Chinese (Simplified, China)
        * zh_hant_tw  - Chinese (Traditional, Taiwan)
        """

        try:
            tds_content_handler = TDSContentHandler()
            tds_reader = TDSReader(tds_content_handler)
            tds_reader.read(tds_file_name)

            output_path = self.get_output_path(tds_file_name)
            self.check_file_writable(output_path)
            new_extract = Extract(output_path)

            collation = self._collation_map[collation]
            table_definition = self._define_table(tds_reader, collation)

            new_extract.addTable('Extract', tableDefinition=table_definition)

            new_extract.close()
            table_definition.close()
        except ReaderException as err:
            raise_with_traceback(WriterException(err))
        except TableauException:
            raise_with_traceback(WriterException(GetLastErrorMessage()))
