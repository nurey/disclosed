# -*- coding: utf-8 -*-
from django.template import Library
from google.appengine.api import users

register = Library()

@register.simple_tag
def google_login_url(redirect='/'):
    return users.create_login_url(redirect)

@register.simple_tag
def google_logout_url(redirect='/'):
    return users.create_logout_url(redirect)
