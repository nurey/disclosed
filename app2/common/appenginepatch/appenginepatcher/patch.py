# -*- coding: utf-8 -*-
from google.appengine.ext import db
import logging, os, sys

def patch_all():
    patch_python()
    patch_app_engine()
    patch_django()
    setup_logging()

def patch_python():
    # Remove modules that we want to override
    for module in ('httplib', 'urllib', 'urllib2', 'memcache',):
        if module in sys.modules:
            del sys.modules[module]

    # For some reason the imp module can't be replaced via sys.path
    from appenginepatcher import have_appserver
    if have_appserver:
        from appenginepatcher import imp
        sys.modules['imp'] = imp

    # Add fake error and gaierror to socket module. Required for boto support.
    import socket
    class error(Exception):
        pass
    class gaierror(Exception):
        pass
    socket.error = error
    socket.gaierror = gaierror

    if have_appserver:
        def unlink(_):
            raise NotImplementedError('App Engine does not support FS writes!')
        os.unlink = unlink

def patch_app_engine():
    # This allows for using Paginator on a Query object. We limit the number
    # of results to 301, so there won't be any timeouts (301 because you can
    # say "more than 300 results").
    def __len__(self):
        return self.count(301)
    db.Query.__len__ = __len__

    # Add "model" property to Query (needed by generic views)
    class ModelProperty(object):
        def __get__(self, query, unused):
            try:
                return query._Query__model_class
            except:
                return query._model_class
    db.Query.model = ModelProperty()

    # Add a few Model methods that are needed for serialization
    def _get_pk_val(self):
        return unicode(self.key())
    db.Model._get_pk_val = _get_pk_val
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._get_pk_val() == other._get_pk_val()
    db.Model.__eq__ = __eq__
    def __ne__(self, other):
        return not self.__eq__(other)
    db.Model.__ne__ = __ne__

    # Make Property more Django-like (needed for serialization)
    db.Property.serialize = True
    db.Property.rel = None
    class Relation(object):
        field_name = 'key_name'
    db.ReferenceProperty.rel = Relation

    # Add repr to make debugging a little bit easier
    def __repr__(self):
        d = dict([(k, getattr(self, k)) for k in self.properties()])
        return '%s(**%s)' % (self.__class__.__name__, repr(d))
    db.Model.__repr__ = __repr__

    # Replace save() method with one that calls put(), so a monkey-patched
    # put() will also work if someone uses save()
    def save(self):
        return self.put()
    db.Model.save = save

    # Add _meta to Model, so porting code becomes easier (generic views,
    # xheaders, and serialization depend on it).
    class _meta(object):
        many_to_many = []
        class pk:
            name = 'key_name'

        def __init__(self, model):
            self.app_label = model.__module__.split('.')[-2]
            self.object_name = model.__name__
            self.module_name = self.object_name.lower()
            self.verbose_name = self.object_name.lower()
            self.verbose_name_plural = None
            self.abstract = False
            self.model = model

        def __str__(self):
            return '%s.%s' % (self.app_label, self.module_name)

        @property
        def local_fields(self):
            return self.model.properties().values()

    # Register models with Django
    old_init = db.PropertiedClass.__init__
    def __init__(cls, name, bases, attrs):
        """Creates a combined appengine and Django model.

        The resulting model will be known to both the appengine libraries and
        Django.
        """
        cls._meta = _meta(cls)
        cls._default_manager = cls
        old_init(cls, name, bases, attrs)
        from django.db.models.loading import register_models
        register_models(cls._meta.app_label, cls)
    db.PropertiedClass.__init__ = __init__

def log_exception(*args, **kwargs):
    logging.exception('Exception in request:')

def patch_django():
    # In order speed things up and consume less memory we lazily replace
    # modules if possible. This requires some __path__ magic. :)

    # Add fake 'appengine' DB backend
    # This also creates a separate datastore for each project.
    from appenginepatcher.db_backends import appengine
    sys.modules['django.db.backends.appengine'] = appengine

    base_path = os.path.abspath(os.path.dirname(__file__))

    # Replace generic views
    from django.views import generic
    generic.__path__.insert(0, os.path.join(base_path, 'generic_views'))

    # Replace db session backend and tests
    from django.contrib import sessions
    sessions.__path__.insert(0, os.path.join(base_path, 'sessions'))
    from django.contrib.sessions import backends
    backends.__path__.insert(0, os.path.join(base_path, 'session_backends'))

    # Replace the dispatchers.
    from django.core import signals

    # Log errors.
    signals.got_request_exception.connect(log_exception)

    # Unregister the rollback event handler.
    import django.db
    signals.got_request_exception.disconnect(django.db._rollback_on_exception)

    # Replace auth models
    # This MUST happen before any other modules import User or they'll
    # get Django's original User model!!!
    from appenginepatcher.auth import models
    sys.modules['django.contrib.auth.models'] = models

    # Replace rest of auth app
    from django.contrib import auth
    auth.__path__.insert(0, os.path.join(base_path, 'auth'))

    # Replace ModelForm
    # This MUST happen as early as possible, but after User got replaced!
    from google.appengine.ext.db import djangoforms as aeforms
    from django import forms
    from django.forms import models as modelforms
    forms.ModelForm = modelforms.ModelForm = aeforms.ModelForm
    forms.ModelFormMetaclass = aeforms.ModelFormMetaclass
    modelforms.ModelFormMetaclass = aeforms.ModelFormMetaclass

    # Fix handling of verbose_name. Google resolves lazy translation objects
    # immedately which of course breaks translation support.
    from django.utils.text import capfirst
    def get_form_field(self, form_class=forms.CharField, **kwargs):
        defaults = {'required': self.required}
        if self.verbose_name:
            defaults['label'] = capfirst(self.verbose_name)
        if self.choices:
            choices = []
            if not self.required or (self.default is None and
                                     'initial' not in kwargs):
                choices.append(('', '---------'))
            for choice in self.choices:
                choices.append((str(choice), unicode(choice)))
            defaults['widget'] = forms.Select(choices=choices)
        if self.default is not None:
            defaults['initial'] = self.default
        defaults.update(kwargs)
        return form_class(**defaults)
    db.Property.get_form_field = get_form_field

    # Extend ModelForm with support for EmailProperty
    def get_form_field(self, **kwargs):
        """Return a Django form field appropriate for an email property."""
        defaults = {'form_class': forms.EmailField}
        defaults.update(kwargs)
        return super(db.EmailProperty, self).get_form_field(**defaults)
    db.EmailProperty.get_form_field = get_form_field

    # Fix default value of UserProperty (Google resolves the user too early)
    def get_form_field(self, **kwargs):
        from django.contrib.auth.models import User
        from django.utils.functional import lazy
        from google.appengine.api import users
        defaults = {'initial': lazy(users.GetCurrentUser, User)}
        defaults.update(kwargs)
        return super(db.UserProperty, self).get_form_field(**defaults)
    db.UserProperty.get_form_field = get_form_field

    # Replace mail backend
    from appenginepatcher import mail as gmail
    from django.core import mail
    mail.SMTPConnection = gmail.GoogleSMTPConnection
    mail.mail_admins = gmail.mail_admins
    mail.mail_managers = gmail.mail_managers

    # Fix translation support if we're in a zip file. We change the path
    # of the django.conf module, so the translation code tries to load
    # Django's translations from the common/django-locale/locale folder.
    from django import conf
    from aecmd import COMMON_DIR
    if '.zip' + os.sep in conf.__file__:
        conf.__file__ = os.path.join(COMMON_DIR, 'django-locale', 'fake.py')

    # Patch login_required if using Google Accounts
    from django.conf import settings
    if 'ragendja.auth.middleware.GoogleAuthenticationMiddleware' in \
            settings.MIDDLEWARE_CLASSES:
        from ragendja.auth.decorators import google_login_required, \
            redirect_to_google_login
        from django.contrib.auth import decorators, views
        decorators.login_required = google_login_required
        views.redirect_to_login = redirect_to_google_login

    # Activate ragendja's GLOBALTAGS support (automatically done on import)
    from ragendja import template

    # Patch auth forms
    from appenginepatcher import auth_forms_patch

    # Add XML serializer
    if not hasattr(settings, 'SERIALIZATION_MODULES'):
        settings.SERIALIZATION_MODULES = {}
    for name in ('xml', 'python', 'json', 'yaml'):
        settings.SERIALIZATION_MODULES[name] = 'appenginepatcher.serializers.' \
            + name

    # Patch DeserializedObject
    from django.core.serializers import base
    class DeserializedObject(base.DeserializedObject):
        def save(self, save_m2m=True):
            self.object.save()
            self.object._parent = None
    base.DeserializedObject = DeserializedObject

def setup_logging():
    from django.conf import settings
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
