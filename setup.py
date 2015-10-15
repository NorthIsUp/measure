#!/usr/bin/env python
from itertools import chain
from setuptools import (
    find_packages,
    setup,
)

PACKAGE_NAME = 'measure'
VERSION = '0.0.0'

requires = {
    'global': [
        'pystatsd',
        'boto3',
    ],
    'setup': [
        'nose>=1.0'
    ],
    'tests': [
        'exam',
        'mock',
    ],
}

requires['all'] = list(set(chain.from_iterable(requires.values()))),


setup(
    author='adam hitchcock',
    author_email='adam@northisup.com',
    url='http://github.com/disqus/measure',
    extras_require=requires,
    name=PACKAGE_NAME,
    packages=find_packages(),
    requires=requires['global'],
    setup_requires=requires['setup'],
    test_suite='nose.collector',
    tests_require=requires['all'],
    version=VERSION,
    zip_safe=False,
)
