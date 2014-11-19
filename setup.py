#!/usr/bin/env python
from setuptools import find_packages, setup
import healthcheck

setup(
    name='healthcheck',
    version=healthcheck.__version__,
    description=healthcheck.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=healthcheck.__url__,
    packages=find_packages(exclude=('tests', '*.tests')),
    tests_require=[
        'Django>=1.4',
        'mock<2.0.0',
        'nose<2.0.0',
        'unittest2<1.0.0',
    ],
)
