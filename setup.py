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

_tableausdk_url_map = {
    '64bit': {
        'Darwin': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-OSX-64Bit-10-1-1.tar.gz',
        'Windows': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Win-64Bit-10-1-1.zip',
        'Linux': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Linux-64Bit-10-1-1.tar.gz',
    },
    '32bit': {
        'Windows': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Win-32Bit-10-1-1.zip',
        'Linux': 'https://downloads.tableau.com/tssoftware/Tableau-SDK-Python-Linux-32Bit-10-1-1.tar.gz',
    }
}

tableau_architecture_url_map = _tableausdk_url_map.get(architecture)

if tableau_architecture_url_map is not None:
    tableau_sdk = tableau_architecture_url_map.get(system)

if tableau_sdk is None:
    raise Exception('Not compatible system')


class TableauSDKInstall(Command):
    """
    Installs TableauSDK.
    """

    description = 'Installs tableausdk according to the platform and architecture.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pip
        pip.main((['install', tableau_sdk]))


setup(
    author='Anurag Agarwal',
    author_email='anurag.agarwal561994@gmail.com',
    description='tableaupy',
    download_url='',
    cmdclass={
        'install_dependencies': TableauSDKInstall,
    },
    entry_points={
        'console_scripts': [
            'auto_extract = tableaupy.cli:main'
        ]
    },
    install_requires=[
        'lxml==4.6.3',
        'pathlib2',
        'click',
        'xmltodict',
        'future',
    ],
    dependency_links=[
        tableau_sdk,
    ],
    license='Apache License (2.0)',
    name='tableaupy',
    packages=[
        'tableaupy',
    ],
    scripts=[],
    setup_requires=[
        'pytest-runner>=2.9,<3.0',
    ],
    test_suite='tests',
    tests_require=[
        'pytest>=3.0.5,<3.1.0',
        'pyyaml>=3.12,<=3.19',
    ],
    url='https://github.com/practo/Tableau-Py',
    version='1.0.0'
)
