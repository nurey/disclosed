from django.contrib import auth
from django.contrib.auth.models import UNUSABLE_PASSWORD, \
    SiteProfileNotAvailable
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from string import ascii_letters, digits
import hashlib, random

def gen_hash(password, salt=None, algorithm='sha512'):
    hash = hashlib.new(algorithm)
    hash.update(password)
    if salt is None:
        salt = ''.join([random.choice(ascii_letters + digits) for _ in range(8)])
    hash.update(salt)
    return (algorithm, salt, hash.hexdigest())

class UserTraits(db.Model):
    last_login = db.DateTimeProperty(verbose_name=_('last login'))
    date_joined = db.DateTimeProperty(auto_now_add=True,
        verbose_name=_('date joined'))
    is_active = db.BooleanProperty(default=False, verbose_name=_('active'))
    is_staff = db.BooleanProperty(default=False,
        verbose_name=_('staff status'))
    is_superuser = db.BooleanProperty(default=False,
        verbose_name=_('superuser status'))
    password = db.StringProperty(default=UNUSABLE_PASSWORD,
        verbose_name=_('password'))

    @property
    def id(self):
        # Needed for compatibility
        return str(self.key())

    def __unicode__(self):
        return unicode(self.key().id_or_name())

    def __str__(self):
        return unicode(self).encode('utf-8')

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def check_password(self, password):
        if not self.has_usable_password():
            return False
        algorithm, salt, hash = self.password.split('$')
        return hash == gen_hash(password, salt, algorithm)[2]

    def set_password(self, password):
        self.password = '$'.join(gen_hash(password))

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    @classmethod
    def make_random_password(self, length=16,
            allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        """
        Generates a random password with the given length and given allowed_chars.
        """
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not settings.AUTH_PROFILE_MODULE:
                raise SiteProfileNotAvailable
            try:
                appname, modelname = settings.AUTH_PROFILE_MODULE.rsplit('.', 1)
                for app in settings.INSTALLED_APPS:
                    if app.endswith('.' + appname):
                        appname = app
                        break
                model = getattr(
                    __import__(appname + '.models', {}, {}, ['']),
                    modelname)
                self._profile_cache = model.all().filter('user =', self).get()
            except ImportError:
                raise SiteProfileNotAvailable
        return self._profile_cache

    def get_group_permissions(self):
        """
        Returns a list of permission strings that this user has through
        his/her groups. This method queries all available auth backends.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self))
        return permissions

    def get_all_permissions(self):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self))
        return permissions

    def has_perm(self, perm):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general.
        """
        # Inactive users have no permissions.
        if not self.is_active:
            return False

        # Superusers have all permissions.
        if self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        for backend in auth.get_backends():
            if hasattr(backend, "has_perm"):
                if backend.has_perm(self, perm):
                    return True
        return False

    def has_perms(self, perm_list):
        """Returns True if the user has each of the specified permissions."""
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app
        label. Uses pretty much the same logic as has_perm, above.
        """
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        for backend in auth.get_backends():
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(self, app_label):
                    return True
        return False

    def get_and_delete_messages(self):
        messages = []
        for m in self.message_set:
            messages.append(m.message)
            m.delete()
        return messages

class EmailUserTraits(UserTraits):
    def email_user(self, subject, message, from_email=None):
        """Sends an e-mail to this user."""
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])

    def __unicode__(self):
        return self.email

class EmailUser(EmailUserTraits):
    email = db.EmailProperty(required=True, verbose_name=_('e-mail address'))
    # This can be used to distinguish between banned users and unfinished
    # registrations
    is_banned = db.BooleanProperty(default=False,
        verbose_name=_('banned status'))

class User(EmailUserTraits):
    """Default User class that mimics Django's User class."""
    username = db.StringProperty(required=True, verbose_name=_('username'))
    email = db.EmailProperty(verbose_name=_('e-mail address'))
    first_name = db.StringProperty(verbose_name=_('first name'))
    last_name = db.StringProperty(verbose_name=_('last name'))
