# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.views import redirect_to_login

LOGIN_REQUIRED_PREFIXES = getattr(settings, 'LOGIN_REQUIRED_PREFIXES', ())
NO_LOGIN_REQUIRED_PREFIXES = getattr(settings, 'NO_LOGIN_REQUIRED_PREFIXES', ())

class LoginRequiredMiddleware(object):
    def process_request(self, request):
        """
        Redirects to login page if request path begins with a
        LOGIN_REQURED_PREFIXES prefix. You can also specify
        NO_LOGIN_REQUIRED_PREFIXES which take precedence.
        """
        if not request.user.is_authenticated():
            for prefix in NO_LOGIN_REQUIRED_PREFIXES:
                if request.path.startswith(prefix):
                    return None
            for prefix in LOGIN_REQUIRED_PREFIXES:
                if request.path.startswith(prefix):
                    return redirect_to_login(request.path)
        return None
