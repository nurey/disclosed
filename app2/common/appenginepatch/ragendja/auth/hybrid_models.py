from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from ragendja.auth.google_models import GoogleUserTraits

class User(GoogleUserTraits):
    """User class that provides support for Django and Google Accounts."""
    user = db.UserProperty()
    username = db.StringProperty(required=True, verbose_name=_('username'))
    email = db.EmailProperty(verbose_name=_('e-mail address'))
    first_name = db.StringProperty(verbose_name=_('first name'))
    last_name = db.StringProperty(verbose_name=_('last name'))

    @classmethod
    def create_djangouser_for_user(cls, user):
        django_user = cls(user=user, email=user.email(),
                          username=user.nickname())
        django_user.put()
        return django_user
