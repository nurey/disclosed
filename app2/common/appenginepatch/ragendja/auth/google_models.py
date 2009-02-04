from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from ragendja.auth.models import EmailUserTraits

class GoogleUserTraits(EmailUserTraits):
    @classmethod
    def get_djangouser_for_user(cls, user):
        django_user = cls.all().filter('user =', user).get()
        if not django_user:
            return cls.create_djangouser_for_user(user)
        return django_user

class User(GoogleUserTraits):
    """Extended User class that provides support for Google Accounts."""
    user = db.UserProperty(required=True)

    @property
    def username(self):
        return self.user.nickname

    @property
    def email(self):
        return self.user.email

    @classmethod
    def create_djangouser_for_user(cls, user):
        django_user = cls(user=user)
        django_user.put()
        return django_user
