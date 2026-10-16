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
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ]
)
