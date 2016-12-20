# pylint: skip-file

"""
Setup script.
"""

from distutils.core import Command
from setuptools import setup

import platform

tableau_sdk = None
system = platform.system()
architecture = platform.architecture()[0]

if architecture == '64bit':
    if system == 'Darwin':
        tableau_sdk = 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-OSX-64Bit-10-1-1.tar.gz'
    elif system == 'Windows':
        tableau_sdk = 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Win-64Bit-10-1-1.zip'
    elif system == 'Linux':
        tableau_sdk = 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Linux-64Bit-10-1-1.tar.gz'
elif architecture == '32bit':
    if system == 'Windows':
        tableau_sdk = 'https://downloads.tableau.com/tssoftware/Tableau-SDK-C-Java-32Bit-10-1-1.zip'
    elif system == 'Linux':
        tableau_sdk = 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Linux-32Bit-10-1-1.tar.gz'

if tableau_sdk is None:
    raise Exception('Not compatible system')


class Coverage(Command):
    """
    Coverage setup.
    """

    description = (
        'Run test suite against single instance of'
        'Python and collect coverage data.'
    )
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import coverage
        import unittest

        cov = coverage.coverage(config_file='.coveragerc')
        cov.erase()
        cov.start()

        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(start_dir='tests')
        unittest.TextTestRunner().run(test_suite)

        cov.stop()
        cov.save()
        cov.report()
        cov.html_report()


setup(
    author='Anurag Agarwal',
    author_email='anurag.agarwal561994@gmail.com',
    description='auto_extract',
    download_url='',
    cmdclass={
        'coverage': Coverage,
    },
    install_requires=[
        'lxml',
        'pathlib2',
    ],
    dependency_link=[
        tableau_sdk,
    ],
    license='Apache License (2.0)',
    name='auto_extract',
    packages=[
        'auto_extract',
    ],
    scripts=[],
    setup_requires=[
        'pytest-runner>=2.9,<3.0',
    ],
    test_suite='tests',
    tests_require=[
        'codecov>=2.0.3,<3.0.0',
        'coverage>=4.0.3,<5.0.0',
        'Sphinx>=1.4.1,<2.0.0',
        'tox>=2.3.1,<3.0.0',
        'virtualenv>=15.0.1,<16.0.0',
        'pytest>=3.0.5,<3.1.0',
    ],
    url='',
    version='1.0.0'
)
