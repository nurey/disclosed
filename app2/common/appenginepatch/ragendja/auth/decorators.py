# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from ragendja.template import render_to_response

def staff_only(view):
    """
    Decorator that requires user.is_staff. Otherwise renders no_access.html.
    """
    @login_required
    def wrapped(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return view(request, *args, **kwargs)
        return render_to_response(request, 'no_access.html')
    return wrapped

def redirect_to_google_login(next, login_url=None, redirect_field_name=None):
    from google.appengine.api import users
    return HttpResponseRedirect(users.create_login_url(next))

def google_login_required(function):
    def login_required_wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            return function(request, *args, **kw)
        return redirect_to_google_login(request.get_full_path())
    return login_required_wrapper
