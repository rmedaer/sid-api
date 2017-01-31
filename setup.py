# -*- coding: utf-8 -*-

""" Default setup tools. """

from setuptools import setup, find_packages

with open('README.md') as f:
    PROJECT_README = f.read()

with open('LICENSE') as f:
    PROJECT_LICENSE = f.read()

setup(
    name='sidapi',
    version='0.1.0',
    description='HTTP API to manage configuration repositories from SID project.',
    long_description=PROJECT_README,
    author='Raphael Medaer (Escaux)',
    author_email='rme@escaux.com',
    url='',
    license=PROJECT_LICENSE,
    packages=find_packages(exclude=('tests', 'docs'))
)
