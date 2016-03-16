#!/usr/bin/env python

from setuptools import setup

setup(name='notemodel',
    version='1.2',
    description='An Automatic Note Modelling Method for Turkish Makam Music Recordings',
    author='Bilge Mirac Atici',
    author_email='miracatici AT gmail DOT com',
    license='agpl 3.0',
    url='https://github.com/miracatici/notemodel.git',
    packages=['notemodel'],
    include_package_data=True,
    install_requires=[
        "numpy",
        "matplotlib",
    ],
)
