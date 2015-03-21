#!/usr/bin/env python
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit(0)

with open('README.rst', 'r') as f:
    long_description = f.read()

# Dynamically calculate the version based on fullcalendar.VERSION.
VERSION = __import__('fullcalendar').get_version()

setup(
    name='mezzanine-fullcalendar',
    version=VERSION,
    url='https://github.com/jonge-democraten/mezzanine-fullcalendar',
    author_email='ict-team@jd.nl',
    description='A Mezzanine calendaring application using the fullcalendar.io '
                'widget.',
    long_description=long_description,
    author='David A Krauth, Jonge Democraten',
    platforms=['any'],
    license='MIT License',
    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ),
    packages=[
        'fullcalendar',
        'fullcalendar.migrations',
        'fullcalendar.templatetags'
    ],
    install_requires=['python-dateutil', 'django>=1.6', 'mezzanine>=3.1']
)
