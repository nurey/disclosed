# -*- coding: utf-8 -*-
from django.contrib.auth.forms import *
from django.utils.translation import ugettext as __

def clean_username(self):
    username = self.cleaned_data["username"]
    if not User.all().filter('username =', username).get():
        return username
    raise forms.ValidationError(__("A user with that username already exists."))
UserCreationForm.clean_username = clean_username

def clean_email(self):
    """
    Validates that a user exists with the given e-mail address.
    """
    email = self.cleaned_data["email"]
    self.users_cache = User.all().filter('email =', email).fetch(100)
    if len(self.users_cache) == 0:
        raise forms.ValidationError(__("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
PasswordResetForm.clean_email = clean_email
