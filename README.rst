distutils_ui
============

A distutils build extension for PyQt{4,5} applications
------------------------------------------------------

Build UI specific elements in tree, controlled by configuration variables in
setup.cfg. Running the tool chain is delegated to a couple of internal build
commands.

Following layout is assumed::

  project/
    i18n/               # keep all translation specific files here
    i18n/project.pro    # translation project file (generated, optionally)
    ui/                 # all designer forms, may contain sub folders
    project.qrc         # project resource definition (generated)
    project_rc.py       # project resources (generated)
  setup.py              # distutils/setuptools module for the project
  setup.cfg             # setup configuration
  ...


Translations
------------
Proper translation is subject of fetching the translatable strings from
all forms and source modules, translate them (with ``linguist``), and convert
the textual representation (``.ts``) into binary form (``.qm``), palatable for
``QTranslator`` instances.

There are two ways to accomplish this task: using an intermediate project
file (``.pro``), that can be generated with the built-in command ``gentrpro``,
or feeding globbing args to the tools ``pylupdate`` and ``lrelease`` directly.
Unfortunately, the latter way is hampered by some bugs. Hence, the preferred way
is using the ``.pro`` file.

Because the translation source files (``.ts``) references forms and sources with
relative paths, and the tools ``pylupdate`` and ``lrelease`` operate relative
to the ``.pro`` file location, and *we* *want* to keep all translation specific
files in one place, we run the translation tool chain relative to ``i18n/``.

A new language
~~~~~~~~~~~~~~
* create an appropriately named file in ``i18n/``
  e.g. ``touch i18n/project_lang.ts``
* build initial translation source with ``setup.py build_ui``
* set up language parameter with linguist once
  e.g. ``linguist i18n/project_lang.ts``

Translation relies on tr() and translate() used properly in the source.


Forms
-----

``ui/`` and sub folders contain all designer forms. You shouldn't mix source
code and forms in one folder, because forms are translated to *Python* source
files, that you want to handle differently (e.g. exclude from translation,
because the translation source is generated from the forms already.

The ``<form>.ui`` file is translated to ``ui_<form>.py``. Usually, it contains
a single form, where the toplevel object is the camel cased name of the
module. E.g.: ``form.ui`` contains a widget ``Form``, that is imported from
toplevel modules with::

    from ui.ui_form import Ui_Form

Typically, this form is subclassed with multiple inheritance::

    class Form(QWidget, Ui_Form):
        def __init__(self, parent = None):
            super(Form, self).__init__(parent)
            self.setupUi(self)


Resources
---------
Resource collection files (``.qrc``) defines resources, that are included within
a single module. Typically, this includes images, translation files (``.qm``),
and other static data. These resources are accessed with::

    app.setWindowIcon(QIcon(":/images/icon.png"))

Note the ":" prefix. The resource file is typically included early in the
main module::

    import project_rc # __IGNORE_WARNING__ (this is not referenced any further)

and the included resources are available in all modules.

**distutils_ui** contains a built-in command ``genqrc``, that generates ``.qrc``
files from globbing patterns. ``genqrc`` supports two specific options: ``prefix``
and ``strip``. Prefix allows to place all resources under a custom prefix, while
strip removes the path from objects. Strip requires, that all files are uniquely
named, otherwise some objects are not accessible. The command ``pyrcc``
generates the resource module ``project_rc.py`` from ``project.qrc``.


Commands
--------
The ``gentrpro`` and ``genqrc`` commands are built-in, therefore they don't
define their own command, rather than process input and output files directly.
All other commands call external tools, that must be available and specified
with a ``command`` parameter in ``setup.cfg``.

Command parameter use ``{macro}`` expressions, that references other parameters
in the same section, such as ``{infiles}`` and ``{outfiles}``, as well as
metadata parameter, like ``{name}`` and ``{version}``. These parameters can
be mixed with file globbing patterns.

``infiles`` and ``outfiles`` parameter define input files and targets.

An ``exclude`` parameter removes matching elements from ``infiles``.

The ``chdir`` parameter allow to change the execution path of that command,
also subject to metadata macro expansion.

A special command mode is provided: ``singlefile``. It is used to call the
command *one* by *one* for *every* input file. In this mode, additional macros
are available, that can be used to further control the output file: ``{path}``,
``{filename}``, and ``{fileext}``. Check the template for ``pyuic`` and
``pyrcc`` commands for examples.

If you only want to work with a command subset: just define ``commands`` in
``[build_ui]`` section accordingly.



setup.py::

    from distutils.command.build import build
    from build_ui import build_ui

    [...]

    cmdclass = {
        'build_ui': build_ui,
    }

    # Optional: inject ui specific build into standard build process
    build.sub_commands.insert(0, ('build_ui', None))

    [...]

    setup(
        name = name,
        version = version,
        [...]
        cmdclass = cmdclass
    )


setup.cfg of build_ui template for PyQt5::

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
    exclude = ../{name}_rc.py

    [pylupdate]
    # update translation source files (*.ts) from forms and source files
    # -noobsolete will remove all outdated translations
    chdir = {name}/i18n
    command = pylupdate5 -verbose {infiles}
    infiles = {name}.pro
    outfiles = {name}_*.ts

    [lrelease]
    # convert translation source files into binary representation (*.qm)
    chdir = {name}/i18n
    command = lrelease-qt5 {infiles}
    infiles = {name}.pro
    outfiles = {name}_*.qm

    [pyuic]
    # generate python source files from UI definitions (*.ui)
    command = pyuic5 -x -o {outfiles} {infiles}
    infiles = {name}/ui/*.ui
    outfiles = {name}/ui/ui_{filename}.py
    singlefile = true

    [genqrc]
    # generate a resource description file (*.qrc)
    chdir = {name}
    infiles = images/*.png i18n/*.qm
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


The plain UI build is triggered with::

    python3 setup.py build_ui [-f|--force]

A cleanup of the generated files can be done in a similar fashion::

    python3 setup.py build_ui [-C|--clean]

Notes:

* avoid spaces in filenames
* '.pro' file approach results in spurious builds

Debug::

    python3 setup.py -v build_ui

Author:

    (c) 2016 Hans-Peter Jansen <hpj@urpla.net>

License:

    MIT, Copyright (c) 2016, Hans-Peter Jansen, see LICENSE.txt
