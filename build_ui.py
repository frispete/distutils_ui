# -*- coding: utf-8 -*-
"""
Distutils/Setuptools build extension for PyQt{4,5} applications

Build UI specific elements in tree, controlled by config vars in setup.cfg.
Running the tool chain is delegated to a couple of internal build commands.

Following layout is assumed:

project/
    i18n/               # keep translation specific files here
    i18n/project.pro    # translation project file (generated)
    ui/                 # all forms, might be organised with subfolders
    project.qrc         # project resource definition (generated)
    project_rc.py       # project resources (generated)

i18n/ contains all files related to internationalisation

    Proper translation is subject of fetching the translatable strings from
    all forms and source modules, translate them (with linguist), and convert
    the textual representation (.ts) into binary form (.qm), palatable for
    QTranslator instances.

    There are two ways to accomplish this task: using an intermediate project
    file (.pro), that can be generated with "gentrpro", or feeding files args
    to the other tools directly. Unfortunately, the latter way is hampered by
    some bugs. Hence, the preferred way is using the .pro file, generated with
    "gentrpro".

    Since the translation source files (.ts) references the forms and sources
    with relative paths, and the tools pylupdate and lrelease operate relative
    to the .pro file location, and _we_ want to keep all translation specific
    files in one place, we run the translation tool chain relative to i18n/.

    A new language is introduced by creating an appropriately named file in
    i18n (e.g. with touch), updating it with "setup.py build_ui", and setting
    up the language parameter with linguist once. Translation relies on tr()
    and translate() used properly, as usual.

ui/ contains all designer forms

    The <forms>.ui are translated to ui_<forms>.py. Usually, they contain a
    single form, where the toplevel object is the camel cased name of the
    module. E.g.: form.ui contains a widget Form, that is imported from main
    project modules with:

        from ui.ui_form import Ui_Form

    Typically, this form is subclassed with multiple inheritance:

        class Form(QWidget, Ui_Form)::
            def __init__(self, parent = None):
                super().__init__(parent)
                self.setupUi(self)

Resources

    project.qrc defines resources, that are included within a single file
    project_rc.py. Typically, this includes images, translation files (.qm), and
    other static data. These resources are accessed with:

        app.setWindowIcon(QIcon(":/images/icon.png"))

    Note the ":" prefix. The resource file is typically included early in the
    main module:

        import project_rc # __IGNORE_WARNING__ (this is not referenced any further)

    and the resources are available in all modules from there on.

    Generating the resource definition with "genqrc" allows further adjustments
    with two specific options: prefix and strip. Prefix allows to place all
    resources under a custom prefix, while strip removes the path from objects.
    Strip requires, that all files are uniquely named, otherwise some objects
    are not accessible.

Commands

    The "gentrpro" and "genqrc" commands are built-in, therefore they doesn't
    define their own command, rather than process input and output files
    directly. All other commands call external tools, that must be available
    and specified with a command parameter in setup.cfg.

    Command parameter use {macro} expressions, that references other parameters
    in the same section, such as {infiles} and {outfiles}, as well as metadata
    parameter, like {name} and {version}. These parameters can be mixed with
    file globbing patterns.

    The "chdir" parameter changes the execution path of that command, also
    subject to metadata macro expansion.

    A special command mode is provided: "singlefile". It is used to call the
    command one by one for every input file. In this mode, additional macros
    are available, that can be used to further control the output file: {path},
    {filename}, and {fileext}. Check template for "pyuic" and "pyrcc" for
    examples.

    If you only want to work with a subset of available commands: just define
    "commands" in [build_ui] accordingly.


setup.py:

from distutils.command.build import build
from build_ui import build_ui

[...]

cmdclass = {
    'build_ui': build_ui,
}

# Optional: inject ui specific build into standard build process
build.sub_commands.insert(0, ('build_ui', None))

setup(
    name = name,
    version = version,
    [...]
    cmdclass = cmdclass
)


setup.cfg of build_ui template:

[build_ui]
# control the tool chain (default: run all commands)
#commands = gentrpro, pylupdate, lrelease, pyuic, genqrc, pyrcc

[gentrpro]
# pro files are processed relative to their location, cope with it:
# generate pro file with relative paths from i18n, and call
# pylupdate and lrelease from within i18n
chdir = {name}/i18n
infiles = ../ui/*.ui ../*.py *.ts
outfiles = {name}.pro

[pylupdate]
# update translation source files (*.ts) from forms and source files
# -noobsolete will remove all outdated translations
chdir = {name}/i18n
command = pylupdate5 -verbose {infiles}
infiles = {name}.pro
outfiles = *.ts

[lrelease]
# convert translation source files into binary representation (*.qm)
chdir = {name}/i18n
command = lrelease-qt5 {infiles}
infiles = {name}.pro
outfiles = *.qm

[pyuic]
# generate python source files from UI definitions (*.ui)
command = pyuic5 -x -o {outfiles} {infiles}
infiles = {name}/ui/*.ui
outfiles = {name}/ui/ui_{filename}.py
singlefile = true

[genqrc]
# generate a resource description file (*.qrc)
chdir = {name}
infiles = images/*.png i18n/*.qm ../README.rst
outfiles = {name}.qrc
# these are specific for genqrc
strip = false
prefix =

[pyrcc]
# generate a resource module from qrc file
command = pyrcc5 -o {outfiles} {infiles}
infiles = {name}/{name}.qrc
outfiles = {name}/{name}_rc.py
singlefile = true


The plain UI build is triggered with:

    python3 setup.py build_ui [-f|--force]

A cleanup of the generated files can be done in a similar fashion:

    python3 setup.py build_ui [-C|--clean]

Notes:

    avoid spaces in filenames

Debug:

    python3 setup.py -v build_ui

Author:

    (c) 2016 Hans-Peter Jansen <hpj@urpla.net>

License:

    BSD 2-Clause

    Copyright (c) 2016, Hans-Peter Jansen, All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.

"""
import os
import sys
import glob
import datetime
import subprocess

from xml.etree import ElementTree
from collections import OrderedDict

from distutils.cmd import Command
from distutils.util import strtobool
from distutils import log


def strsplit(msg, splitter = ' '):
    return [s for s in map(lambda s: s.strip(), msg.split(splitter)) if s]

strlist = lambda list, joiner = ' ': joiner.join(list)

ftime = lambda t: datetime.datetime.fromtimestamp(t).isoformat(' ')



def indentXML(elem, level = 0):
    ind = "\n" + level * " "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = ind + " "
        for e in elem:
            indentXML(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = ind + " "
        if not e.tail or not e.tail.strip():
            e.tail = ind
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = ind


class build_tool(Command):
    """base class for all internal commands"""
    description = 'generic build tool class'
    # we inherit the force flag from build_ui
    user_options = []

    def initialize_options(self):
        self.debug('%s.initialize_options', self.__class__.__name__)
        self.command = None
        self.infiles = None
        self.outfiles = None
        self.singlefile = None
        self.exclude = None
        self.chdir = None
        # internal
        self._cwd = None
        self._vars = {}
        self._chkfiles = {}

    def finalize_options(self):
        self.debug('%s.finalize_options', self.__class__.__name__)
        if self.singlefile is not None:
            self.singlefile = strtobool(self.singlefile)
        # inherit these from build_ui
        self.force = self.parent.force
        self.clean = self.parent.clean
        # build vars dict from metadata
        for attr in ('name', 'version'):
            self._vars[attr] = getattr(self.distribution.metadata, 'get_' + attr)()
        if self.exclude is None:
            self.exclude = []
        else:
            self.exclude = self.parse_file_args('exclude', strsplit(self.exclude))
        self.chdir = self.parse_arg('chdir', self.chdir or '')
        # subprocess environment: run tools in posix locale
        self.env = dict(os.environ)
        self.env['LANG'] = b'C'

    def run(self):
        self.debug('%s.run', self.__class__.__name__)
        #from pprint import pformat
        #self.debug('%s.run: %s', self.__class__.__name__, pformat(self.__dict__))

        if self.chdir:
            self._cwd = os.getcwd()
            os.chdir(self.chdir)

        # infiles
        infiles = self.parse_file_args('infiles', strsplit(self.infiles or ''))

        # filter excludes
        infiles = [f for f in infiles if f not in self.exclude]

        # run command(s)
        if self.singlefile:
            for infile in infiles:
                self.process_file(infile)
        else:
            self.process_files(infiles)

        if self._cwd:
            os.chdir(self._cwd)

    def process_file(self, infile):
        vars = dict(self._vars)

        # infile
        vars['infiles'] = infile
        path, filename = os.path.split(infile)
        filename, fileext = os.path.splitext(filename)
        vars['path'] = path
        vars['filename'] = filename
        vars['fileext'] = fileext

        # outfile
        outfile = strsplit(self.outfiles or '')
        outfile = self.parse_file_args('outfiles', outfile, vars)
        if len(outfile) > 1:
            self.warn('process_file: outfiles should never expand to more '
                      'than one file in singlefile mode: %s', str(outfile))
        outfile = outfile[0]
        vars['outfiles'] = outfile

        # clean up
        if self.clean:
            self.cleanup([outfile])
            return

        # make sure, outfile directory exists
        self.makedirs(os.path.dirname(outfile))

        # check timestamps
        if not self.force:
            if not self.newer([infile], [outfile]):
                self.debug('process_file: "%s" is newer than "%s"', outfile, infile)
                return

        # run command
        self.run_command(self.command, vars)

    def process_files(self, infiles):
        vars = dict(self._vars)

        # infiles
        vars['infiles'] = strlist(infiles)

        # outfiles
        outfiles = strsplit(self.outfiles or '')
        outfiles = self.parse_file_args('outfiles', outfiles, vars)
        vars['outfiles'] = strlist(outfiles)

        # clean up
        if self.clean:
            self.cleanup(outfiles)
            return

        # make sure, outfile directories exist
        for outfile in outfiles:
            self.makedirs(os.path.dirname(outfile))

        # check timestamps
        if not self.force:
            if not self.newer(infiles, outfiles):
                self.debug('process_files: outfiles are newer than infiles')
                return

        # run command
        self.run_command(self.command, vars)

    def run_command(self, command, vars = None):
        if vars is None:
            vars = self.vars
        if not command:
            self.fatal('run_command: mandatory config value for <command> missing')
        # assemble command
        command = self.parse_arg('command', command, vars)
        self.info('run_command: "%s"', command)
        try:
            ret = subprocess.call(command.split(' '), env = self.env)
        except OSError as e:
            self.error('run_command: %s', e)
        else:
            if ret != 0:
                self.error('run_command "%s" returned: %d', command, ret)

    def makedirs(self, path):
        if path and not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                self.error('makedirs failed: %s', e)

    def cleanup(self, files):
        for file in files:
            if os.path.exists(file):
                os.unlink(file)
                self.info('cleanup: "%s" removed', file)

    def parse_file_args(self, command, args, vars = None):
        if vars is None:
            vars = self._vars
        self.debug('parse_file_args: %s: "%s" %s', command, args, vars)
        ret = []
        for arg in args:
            arg = self.parse_arg(command, arg, vars)
            # if arg is a globbing pattern, add matched items
            # otherwise, add the arg itself
            items = glob.glob(arg)
            if items:
                ret.extend(items)
            else:
                ret.append(arg)
        self.debug('parse_file_args: %s: "%s"', command, ret)
        return ret

    def parse_arg(self, command, arg, vars = None):
        if vars is None:
            vars = self._vars
        self.debug('parse_arg: %s: "%s" %s', command, arg, vars)
        try:
            arg = arg.format(**vars)
        except KeyError as e:
            self.error('%s: %s', command, e)
        else:
            self.debug('parse_arg: %s: "%s"', command, arg)
            return arg

    def newer(self, sources, targets):
        for target in targets:
            if not os.path.exists(target):
                self.debug('newer: %s does not exist', target)
                return True
        srctime = 0
        srcfile = None
        for source in sources:
            mtime = os.stat(source).st_mtime
            srctime = max(mtime, srctime)
            if mtime == srctime:
                srcfile = source
        tgttime = 0
        tgtfile = None
        for target in targets:
            mtime = os.stat(target).st_mtime
            tgttime = max(mtime, tgttime)
            if mtime == tgttime:
                tgtfile = target
        ret = srctime >= tgttime

        self.debug('newer: %s %s (%s) is %s than %s (%s)',
                    ret, srcfile, ftime(srctime),
                    ret and 'newer' or 'older',
                    tgtfile, ftime(tgttime))

        return ret

    def debug(self, msg, *args):
        log.debug(self.__class__.__name__ + '.' + msg, *args)

    def info(self, msg, *args):
        log.info(self.__class__.__name__ + '.' + msg, *args)

    def warn(self, msg, *args):
        log.warn(self.__class__.__name__ + '.' + msg, *args)

    def error(self, msg, *args):
        log.error(self.__class__.__name__ + '.' + msg, *args)

    def fatal(self, msg, *args):
        log.error(self.__class__.__name__ + '.' + msg, *args)
        sys.exit(1)


class gentrpro(build_tool):
    def run_command(self, command, vars = None):
        if vars is None:
            vars = self.vars
        infiles = strsplit(vars["infiles"])
        outfile = vars["outfiles"]
        self.gentrpro(infiles, outfile)

    def gentrpro(self, infiles, outfile):
        forms = []
        sources = []
        translations = []
        extmap = {
            '.ui': forms,
            '.py': sources,
            '.pyw': sources,
            '.ts': translations,
        }

        for item in infiles:
            lst = extmap.get(os.path.splitext(item)[1])
            if lst is not None:
                if item in lst:
                    self.warn('gentrpro: duplicate "%s" ignored', item)
                else:
                    lst.append(item)
            else:
                self.warn('gentrpro: extension of "%s" is not supported, ignored', item)

        with open(outfile, 'wb') as fd:
            for item in sorted(forms):
                fd.write(('FORMS += %s\n' % item).encode('utf-8'))
            for item in sorted(sources):
                fd.write(('SOURCES += %s\n' % item).encode('utf-8'))
            for item in sorted(translations):
                fd.write(('TRANSLATIONS += %s\n' % item).encode('utf-8'))

        self.info('gentrpro: "%s" generated', outfile)


class genqrc(build_tool):
    def initialize_options(self):
        super().initialize_options()
        self.prefix = None
        self.strip = None

    def finalize_options(self):
        super().finalize_options()
        if self.strip is not None:
            self.strip = strtobool(self.strip)

    def run_command(self, command, vars = None):
        if vars is None:
            vars = self.vars
        infiles = strsplit(vars["infiles"])
        outfile = vars["outfiles"]
        self.genqrc(infiles, outfile)

    def genqrc(self, infiles, outfile):
        items = OrderedDict()

        for item in infiles:
            key = item
            if self.strip:
                key = os.path.basename(item)
            if key in items:
                self.warn('genqrc: "%s" is duplicate from "%s": ignored', key, items[key])
            else:
                items[key] = item

        qrc = ElementTree.Element('qresource')
        if self.prefix is not None:
            qrc.set('prefix', self.prefix)
        for key, item in items.items():
            file = ElementTree.Element('file')
            file.text = item
            if item != key:
                file.set('alias', key)
            qrc.append(file)
        rcc = ElementTree.Element('RCC')
        rcc.append(qrc)
        indentXML(rcc)

        with open(outfile, 'wb') as fd:
            xml = ElementTree.tostring(rcc, encoding = 'utf-8')
            fd.write(xml + b'\n')

        self.info('genqrc: "%s" generated', outfile)


class pylupdate(build_tool):
    # prevent the *.ts files from being removed
    def cleanup(self, files):
        pass

class lrelease(build_tool):
    pass

class pyuic(build_tool):
    pass

class pyrcc(build_tool):
    pass


class build_ui(Command):
    """top level command class, that just calls the internal commands"""
    description = 'call the various PyQt specific build tools'
    user_options = [
        ('force', 'f', 'forcibly build everything (ignore file timestamps)'),
        ('commands=', 'c', 'comma separated list of commands to execute'),
        ('clean', 'C', 'remove generated files'),
    ]
    all_commands = ['gentrpro', 'pylupdate', 'lrelease', 'pyuic', 'genqrc', 'pyrcc']

    def initialize_options(self):
        log.debug('%s.initialize_options', self.__class__.__name__)
        self.force = None
        self.commands = None
        self.clean = None

    def finalize_options(self):
        log.debug('%s.finalize_options', self.__class__.__name__)
        self.commands = self.commands and strsplit(self.commands, ',') or self.all_commands
        # create build_tool command instances
        for cmd in self.commands:
            inst = globals().get(cmd)
            inst.parent = self
            self.distribution.cmdclass[cmd] = inst

    def run(self):
        log.debug('%s.run', self.__class__.__name__)
        for cmd in self.commands:
            log.debug('%s.run: execute "%s"', self.__class__.__name__, cmd)
            self.run_command(cmd)
