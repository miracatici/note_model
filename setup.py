#!/usr/bin/env python

from setuptools import setup

setup(name='note_model',
      version='0.1',
      description='An Automatic Note Modelling Method for Turkish Makam Music Recordings',
      author='Bilge Mirac Atici',
      url='https://github.com/miracatici/note_model.git',
      packages=['note_model'], requires=['tonic_identifier']
      )
