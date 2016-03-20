#! /usr/bin/env python3
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README')) as f:
    long_description = f.read()

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
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
    	    'prepare = crumhorn.prepare:main',
            'cleanup = crumhorn.cleanup:main',
        ]
    }

)