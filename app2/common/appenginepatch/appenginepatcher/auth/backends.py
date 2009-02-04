# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

try: 
    set 
except NameError: 
    from sets import Set as set # Python 2.3 fallback
 	
class ModelBackend(object):
    def authenticate(self, username=None, password=None):
        user = User.all().filter('username = ', username).get()
        if not user:
            user = User.all().filter('email =', username).get()
        if user and user.check_password(password):
            return user
        return None

    def get_group_permissions(self, user_obj):
        return set()

    def get_all_permissions(self, user_obj):
        return set()

    def has_perm(self, user_obj, perm):
        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj, app_label):
        for perm in self.get_all_permissions(user_obj): 
            if perm[:perm.index('.')] == app_label: 
                return True 
        return False 

    def get_user(self, user_id):
        return User.get(user_id)
