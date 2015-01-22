#!/usr/bin/env python
from setuptools import find_packages, setup
import healthcheck


test_requirements = open('requirements.txt').read().split('\n')

setup(
    name='healthcheck',
    version=healthcheck.__version__,
    description=healthcheck.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=healthcheck.__url__,
    packages=find_packages(exclude=('tests', '*.tests')),
    setup_requires=['nose < 2.0.0'],
    tests_require=test_requirements,
)
