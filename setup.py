# -*- coding: utf-8 -*-

# setup.py
###############################################################################
# Written by Arno Simons

# Released under GNU General Public License, version 3.0

# Copyright (c) 2017 Arno Simons

# This file is part of Intertext.

# Intertext is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any
 # later version.

# Intertext is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with 
# Intertext. If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# Always prefer setuptools over distutils
from setuptools import setup #, find_packages
# To use a consistent encoding
from codecs import open
import os



VERSION = '0.0.1'
INSTALL_REQUIRES = [
    'networkx>1,<2',
    'textacy',
    'gensim',
    'pyzotero',
    'distance',
    'ftfy',
]

__dir__ = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(__dir__, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='intertext',
    packages = ['intertext'],

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,

    description='tools for relational discourse analysis',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/arnosimons/intertext',
    download_url = 'https://github.com/arnosimons/intertext/archive/{}.tar.gz'.format(VERSION),

    # Author details
    author='Arno Simons',

    # Choose your license
    license='GPLv3',

    # # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

    #     # Indicate who your project is intended for
    #     'Intended Audience :: Developers',
        'Topic :: Sociology',

    #     # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

    #     # Specify the Python versions you support here. In particular, ensure
    #     # that you indicate whether you support Python 2, Python 3 or both.
    #     'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.3',
    #     'Programming Language :: Python :: 3.4',
    #     'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='''
        intertext, 
        discourse analysis, 
        network analysis, 
        citation analysis, 
        textmining,
        text processing,
        zotero,
        bibliometrics,
        scientometrics,
        nlp''',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['docs', 'tests', 'release_and_install', 'issues', 'dist']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    # py_modules=["intertext"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    
    install_requires=INSTALL_REQUIRES,

    # # List additional groups of dependencies here (e.g. development
    # # dependencies). You can install these using the following syntax,
    # # for example:
    # # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # # If there are data files included in your packages that need to be
    # # installed, specify them here.  If using Python 2.6 or less, then these
    # # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # # Although 'package_data' is the preferred approach, in some case you may
    # # need to place data files outside of your packages. See:
    # # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # # To provide executable scripts, use entry points in preference to the
    # # "scripts" keyword. Entry points provide cross-platform support and allow
    # # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)