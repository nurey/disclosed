# -*- coding: utf-8 -*-
import os, sys

COMMON_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.dirname(COMMON_DIR)
ZIP_PACKAGES_DIRS = (os.path.join(PROJECT_DIR, 'zip-packages'),
                     os.path.join(COMMON_DIR, 'zip-packages'))

def setup_env(manage_py_env=False):
    """Configures app engine environment for command-line apps."""
    # Try to import the appengine code from the system path.
    try:
        from google.appengine.api import apiproxy_stub_map
    except ImportError, e:
        # Not on the system path. Build a list of alternative paths where it
        # may be. First look within the project for a local copy, then look for
        # where the Mac OS SDK installs it.
        paths = [os.path.join(COMMON_DIR, '.google_appengine'),
                 '/usr/local/google_appengine']
        for path in os.environ.get('PATH', '').replace(';', ':').split(':'):
            path = path.rstrip(os.sep)
            if path.endswith('google_appengine'):
                paths.append(path)
        if os.name in ('nt', 'dos'):
            prefix = '%(PROGRAMFILES)s' % os.environ
            paths.append(prefix + r'\Google\google_appengine')
        # Loop through all possible paths and look for the SDK dir.
        SDK_PATH = None
        for sdk_path in paths:
            if os.path.exists(sdk_path):
                SDK_PATH = sdk_path
                break
        if SDK_PATH is None:
            # The SDK could not be found in any known location.
            sys.stderr.write("The Google App Engine SDK could not be found!\n")
            sys.stderr.write("See README for installation instructions.\n")
            sys.exit(1)
        # Add the SDK and the libraries within it to the system path.
        EXTRA_PATHS = [
            SDK_PATH,
            os.path.join(SDK_PATH, 'lib', 'antlr3'),
            os.path.join(SDK_PATH, 'lib', 'webob'),
            os.path.join(SDK_PATH, 'lib', 'yaml', 'lib'),
        ]
        # Add the SDK's Django version if the user didn't override it.
        if not (os.path.isdir(os.path.join(COMMON_DIR, 'django')) or
                os.path.isdir(os.path.join(PROJECT_DIR, 'django'))):
            EXTRA_PATHS.append(os.path.join(SDK_PATH, 'lib', 'django'))
        sys.path = EXTRA_PATHS + sys.path
        from google.appengine.api import apiproxy_stub_map

    # Add this folder to sys.path
    sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

    setup_project()

    from appenginepatcher.patch import patch_all
    patch_all()

    if not manage_py_env:
        return

    # The following should only be done after patch_all()

    # Disable Model validation
    from django.core.management import validation
    validation.get_validation_errors = lambda x, y=0: 0

    # Remove unsupported commands
    from django.core import management
    FindCommandsInZipfile.orig = management.find_commands
    management.find_commands = FindCommandsInZipfile
    management.get_commands()
    for cmd in management._commands.keys():
        if cmd.startswith('sql') or cmd in ('adminindex', 'createcachetable',
                'dbshell', 'inspectdb', 'runfcgi', 'syncdb', 'validate',):
            del management._commands[cmd]

def FindCommandsInZipfile(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    This implementation also works when Django is loaded from a zip.

    Returns an empty list if no commands are defined.
    """
    zip_marker = '.zip' + os.sep
    if zip_marker not in management_dir:
        return FindCommandsInZipfile.orig(management_dir)

    import zipfile
    # Django is sourced from a zipfile, ask zip module for a list of files.
    filename, path = management_dir.split(zip_marker)
    zipinfo = zipfile.ZipFile(filename + '.zip')

    # The zipfile module returns paths in the format of the operating system
    # that created the zipfile! This may not match the path to the zipfile
    # itself. Convert operating system specific characters to '/'.
    path = path.replace('\\', '/')
    def _IsCmd(t):
        """Returns true if t matches the criteria for a command module."""
        t = t.replace('\\', '/')
        return t.startswith(path) and not os.path.basename(t).startswith('_') \
            and t.endswith('.py')

    return [os.path.basename(f)[:-3] for f in zipinfo.namelist() if _IsCmd(f)]

def setup_project():
    from appenginepatcher import on_production_server

    # Remove the standard version of Django if the user wants to override it.
    if 'django' in sys.modules and sys.modules['django'].VERSION[0] < 1:
        for k in [k for k in sys.modules if k.startswith('django')]:
            del sys.modules[k]

    # We must set this env var *before* importing any part of Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    if on_production_server:
        # This fixes pwd import bug for os.path.expanduser()
        os.environ['HOME'] = PROJECT_DIR

    # Add the two parent folders and appenginepatcher's lib folder to sys.path.
    # The current folder has to be added in main.py or setup_env(). This
    # suggests a folder structure where you separate reusable code from project
    # code:
    # project -> common -> appenginepatch
    # You can put a custom Django version into the "common" folder, for example.
    EXTRA_PATHS = [
        PROJECT_DIR,
        COMMON_DIR,
    ]

    # We have to import this here, so the stubs use the original Python libs
    # and we can override them for the rest of the code below.
    try:
        from google.appengine.tools import appcfg
        from google.appengine.api import urlfetch_stub
    except ImportError:
        pass

    # Don't yet patch httplib if we'll execute a dev_appserver because
    # urlfetch would get reloaded and then use the wrong httplib.
    this_folder = os.path.abspath(os.path.dirname(__file__))
    EXTRA_PATHS.append(os.path.join(this_folder, 'appenginepatcher', 'lib'))

    # We support zipped packages in the common and project folders.
    # The files must be in the packages folder.
    for packages_dir in ZIP_PACKAGES_DIRS:
        if os.path.isdir(packages_dir):
            for zip_package in os.listdir(packages_dir):
                EXTRA_PATHS.append(os.path.join(packages_dir, zip_package))

    sys.path = EXTRA_PATHS + sys.path
