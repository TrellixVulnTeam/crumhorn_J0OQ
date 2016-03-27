#! /usr/bin/env python3
# coding=utf-8
from os import path

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


class UseToxError(TestCommand):
    def run_tests(self):
        raise RuntimeError('Run tests with tox')


setup(
    name='crumhorn',
    version='0.0.1',
    description='A pipeline for building and managing personal cloud images',
    long_description=long_description,
    url='https://github.com/jelford/crumhorn',
    author='James Elford',
    author_email='james.p.elford@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'python-digitalocean>=1.8,<2',
        'toml~=0.9'
    ],
    tests_require=[
        'pytest~=2.9'
    ],
    setup_requires=[
    ],
    entry_points={
        'console_scripts': [
            'prepare = crumhorn.prepare:main',
            'cleanup = crumhorn.cleanup:main',
            'launch = crumhorn.launch:main',
            'compile = crumhorn.compile:main'
        ]
    },
    cmdclass={'test': UseToxError}
)
