# -*- coding: utf8 -*-

from setuptools import setup, find_packages

from distutils.command.build import build
from distutils_ui.build_ui import build_ui

cmdclass = {
    'build_ui': build_ui,
}

# Inject ui specific build into standard build process
build.sub_commands.insert(0, ('build_ui', None))

setup(
    name = 'example',
    version = '0.1',
    description = 'PyQt-Example',
    long_description = 'PyQt-Example Build Test',
    author = 'Hans-Peter Jansen',
    author_email = 'hp@lisa-gmbh.de',
    # url = ,
    license = 'MIT',
    packages = find_packages(),
    cmdclass = cmdclass,
)
