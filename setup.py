#!/usr/bin/env python
from setuptools import find_packages, setup
import healthcheck

with open('requirements.txt') as requirements_file:
    test_requirements = requirements_file.readlines()

setup(
    name='healthcheck',
    version=healthcheck.__version__,
    description=healthcheck.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=healthcheck.__url__,
    packages=find_packages(exclude=('tests', '*.tests')),
    tests_require=test_requirements,
    test_suite='nose.collector',
)
