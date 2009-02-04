# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models.manager import EmptyManager
from google.appengine.ext import db
from django.contrib.auth.models import *

AUTH_USER_MODULE = getattr(settings, 'AUTH_USER_MODULE', None)
if AUTH_USER_MODULE:
    User = __import__(AUTH_USER_MODULE, {}, {}, ['']).User
    if User._meta.app_label != 'auth':
        # Remove ragendja's auth.user model registration from Django
        from django.db.models.loading import cache
        del cache.app_models['auth']['user']
else:
    from ragendja.auth.models import User

class Message(db.Model):
    """User message model"""
    user = db.ReferenceProperty(User)
    message = db.TextProperty()

class Group(db.Model):
    """Group model not fully implemented yet."""
    # TODO: Implement this model, requires contenttypes
    name = db.StringProperty()
    permissions = EmptyManager()

class Permission(db.Model):
    """Permission model not fully implemented yet."""
    # TODO: Implement this model, requires contenttypes
    name = db.StringProperty()
