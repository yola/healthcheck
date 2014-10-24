#!/usr/bin/env python
from setuptools import setup
import healthcheck

setup(
    name='healthcheck',
    version=healthcheck.__version__,
    description=healthcheck.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    url=healthcheck.__url__,
    packages=['healthcheck'],
)

