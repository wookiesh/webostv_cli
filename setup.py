#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='webostv-cli',
      version='0.1dev',
      description='Get control over that evil box',
      long_description=open('README.md').read(),   
      author='Joseph Piron',
      author_email='joseph@miom.be',
      url='https://www.github.com/eagleamon/webostv-cli',
      packages=find_packages(),
      python_requires='>=3.4.*',
      install_requires=[
          'click>=7.0',
          'pywebostv>=0.8.4',
          'pynput>=1.4.2',
          'wakeonlan>=1.1.6'
      ],
      entry_points={
          'console_scripts': [
              'lg=webostv_cli:main'
          ]
      }
      )
