# -*- coding: utf8 -*-
# vim:set et ts=8 sw=4:

from setuptools import setup

from distutils_ui import __version__ as version

with open('README.rst', 'r') as fd:
    long_description = fd.read()

setup(
    name = 'distutils_ui',
    version = version,
    description = 'A distutils build extension for PyQt{4,5} applications',
    long_description = long_description,
    author = 'Hans-Peter Jansen',
    author_email = 'hpj@urpla.net',
    url = 'https://github.com/frispete/distutils_ui',
    license = 'MIT',
    keywords = 'distutils setuptools generate translate build resources',
    packages = ['distutils_ui'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Framework :: Setuptools Plugin',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: System :: Software Distribution',
    ],
)
