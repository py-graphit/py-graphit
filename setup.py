#! /usr/bin/env python
# -*- coding: utf-8 -*-

# package: graphit
# file: setup.py
#
# A Python graph based data modeling library
#
# Copyright © 2016 Marc van Dijk, VU University Amsterdam, the Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py-graphit',
    version="0.2.1",
    description='Graph based data handling for the MDStudio application',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Marc van Dijk - VU University - Amsterdam,',
    author_email='m4.van.dijk@vu.nl',
    url='https://graphit.github.io',
    license='Apache Software License 2.0',
    keywords='graph data ORM',
    platforms=['Any'],
    packages=find_packages(),
    py_modules=['graphit'],
    test_suite="tests",
    install_requires=['uritools', 'pytz', 'python-dateutil'],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
    ],
    extras_require={
        'test': ['coverage', 'PyYAML']
    }
)
