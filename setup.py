#!/usr/bin/env python
import sys
from itertools import chain

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


PACKAGE_NAME = 'measure'
VERSION = '0.4.0'

requires = {
    'global': [
        'pystatsd',
        'boto3',
    ],
    'tests': [
        'mock',
        'pytest',
        'django',
    ],
    'develop': [
        'flake8',
        'autopep8',
    ]
}


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


requires['all'] = list(set(chain.from_iterable(requires.values()))),

setup(
    author='adam hitchcock',
    author_email='adam@northisup.com',
    cmdclass={'test': PyTest},
    url='http://github.com/disqus/measure',
    extras_require=requires,
    name=PACKAGE_NAME,
    packages=find_packages(),
    requires=requires['global'],
    test_suite='nose.collector',
    tests_require=requires['all'],
    version=VERSION,
    zip_safe=False,
)
