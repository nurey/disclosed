# -*- coding: utf-8 -*-
from appenginepatcher import on_production_server
import os
DEBUG = not on_production_server
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
    ('Ilia Lobsanov', 'samogon@gmail.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'appengine'

MEDIA_URL = '/media/'

# Email server settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'user@localhost'
SERVER_EMAIL = 'user@localhost'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'ragendja.template.app_prefixed_loader',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'ragendja.middleware.LoginRequiredMiddleware',
#    'ragendja.auth.middleware.GoogleAuthenticationMiddleware',
)

#AUTH_USER_MODULE = 'ragendja.auth.google_models'
#AUTH_ADMIN_MODULE = 'ragendja.auth.google_admin'

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.webdesign',
    'appenginepatcher',
    'goat',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

CACHE_BACKEND = 'memcached://?timeout=0'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1267845633'

# ENABLE_PROFILER = True
# PROFILE_PATTERN = '.*contract_count.*' # matches all function names containing 'token'
# MAX_PROFILE_RESULTS = 1160 # default is 80

