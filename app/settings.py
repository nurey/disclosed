"""Minimal Django settings."""

import os

APPEND_SLASH = False
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
INSTALLED_APPS = (
    'goat',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # see http://groups.google.com/group/google-appengine/browse_thread/thread/eb6ca5ebf850b84d#
)
ROOT_URLCONF = 'urls'
TEMPLATE_CONTEXT_PROCESSORS = ()
TEMPLATE_DEBUG = DEBUG
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    )
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    )
