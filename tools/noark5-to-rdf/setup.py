#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='noark5tordf',
      version='1.0.0',
      description='Tool for converting NOARK5 compliant XML files to RDF',
      author='Graham Moore',
      author_email='graham.moore@sesam.io',
      url='http://sesam.io',
      packages=['noark5tordf'],      
      install_requires=['pyyaml>=3.11','nose'],
      test_suite = 'nose.collector',
      license = "BSD",
      keywords = "convert noark5 xml rdf",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
        "Operating System :: POSIX",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Markup :: XML",
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
      ],
      entry_points={
          'console_scripts': [
              'noark5tordf=noark5tordf.noark5tordf:main',
          ],
      })
