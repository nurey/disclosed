# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation
from django.utils.encoding import force_unicode
from google.appengine.ext import db
from ragendja.dbutils import transaction

class Session(db.Model):
    data = db.BlobProperty()
    expiry = db.DateTimeProperty()

class SessionStore(SessionBase):
    """A key-based session store for Google App Engine."""

    def load(self):
        session = self._gae_get_session(self.session_key)
        if session:
            try:
                return self.decode(force_unicode(session.data))
            except SuspiciousOperation:
                # Create a new session_key for extra security.
                pass
        self.create()
        return {}

    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        self._save(must_create, self._get_session(no_load=must_create))

    @transaction
    def _save(self, must_create, session):
        if must_create and Session.get_by_key_name('k:' + self.session_key):
            raise CreateError
        session = Session(key_name='k:' + self.session_key,
            data=self.encode(session),
            expiry=self.get_expiry_date())
        session.put()

    def exists(self, session_key):
        return self._gae_get_session(session_key) is not None

    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        session = self._gae_get_session(session_key)
        if session:
            session.delete()

    def _gae_get_session(self, session_key):
        session = Session.get_by_key_name('k:' + session_key)
        if session:
            if session.expiry > datetime.now():
                return session
            session.delete()
        return None
