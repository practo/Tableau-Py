# -*- coding: utf-8 -*-
"""Define configurations and file paths"""
import os

TEST_RESULTS_PATH = 'tests/resources'

TEST_DS_RESULT_COLUMN_DEFINITION_PATH = os.path.join(
    TEST_RESULTS_PATH,
    'sample-datasource-column-definitions.yaml'
)

TEST_DS_RESULT_METADATA_PATH = os.path.join(
    TEST_RESULTS_PATH,
    'sample-datasource-metadata-definition.yaml'
)

SAMPLE_PATH = 'sample'
SAMPLE_DS_PATH = os.path.join(SAMPLE_PATH, 'sample.tds')
