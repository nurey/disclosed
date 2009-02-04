# -*- coding: utf-8 -*-
from django.http import Http404
from google.appengine.ext import db
from ragendja.pyutils import getattr_by_path
from random import choice
from string import ascii_letters, digits

def get_filters(*filters):
    """Helper method for get_filtered."""
    if len(filters) % 2 == 1:
        raise ValueError('You must supply an even number of arguments!')
    return zip(filters[::2], filters[1::2])

def get_filtered(data, *filters):
    """Helper method for get_xxx_or_404."""
    for filter in get_filters(*filters):
        data.filter(*filter)
    return data

def get_object_or_404(model, *filters_or_key, **kwargs):
    if kwargs.get('key_name'):
        item = model.get_by_key_name(kwargs.get('key_name'))
    elif kwargs.get('id'):
        item = model.get_by_id(kwargs.get('id'))
    elif len(filters_or_key) > 1:
        item = get_filtered(model.all(), *filters_or_key).get()
    else:
        item = model.get(filters_or_key[0])
    if not item:
        raise Http404('Object does not exist!')
    return item

def get_list_or_404(model, filters):
    data = get_filtered(model.all(), *filters)
    if not data.get():
        raise Http404('No objects found!')
    return data

KEY_NAME_PREFIX = 'k'
def generate_key_name(*values):
    """
    Escapes a string such that it can be used safely as a key_name.
    
    You can pass multiple values in order to build a path.
    """
    return KEY_NAME_PREFIX + '/'.join(
        [value.replace('%', '%1').replace('/', '%2') for value in values])

def transaction(func):
    """Decorator that always runs the given function in a transaction."""
    def _transaction(*args, **kwargs):
        return db.run_in_transaction(func, *args, **kwargs)
    return _transaction

@transaction
def db_add(model, key_name, parent=None, **kwargs):
    """
    This function creates an object transactionally if it does not exist in
    the datastore. Otherwise it returns None.
    """
    existing = model.get_by_key_name(key_name, parent=parent)
    if not existing:
        new_entity = model(parent=parent, key_name=key_name, **kwargs)
        new_entity.put()
        return new_entity
    return None

def db_create(model, parent=None, key_name_format=u'%s', **kwargs):
    """
    Creates a new model instance with a random key_name and puts it into the
    datastore.
    """
    charset = ascii_letters + digits
    while True:
        # The key_name is 16 chars long. Make sure that the first char doesn't
        # begin with a digit.
        key_name = key_name_format % (choice(ascii_letters) +
            ''.join([choice(charset) for i in range(15)]))
        result = db_add(model, key_name, parent=parent, **kwargs)
        if result:
            return result

def prefetch_references(object_list, references):
    """
    Dereferences the given (Key)ReferenceProperty fields of a list of objects
    in as few get() calls as possible.
    """
    # TODO: There is no safe way to work with the cache of a ReferenceProperty,
    # so we don't yet support this.
    if object_list and references:
        if not isinstance(references, (list, tuple)):
            references = (references,)
        model = object_list[0].__class__
        targets = {}
        # Collect models and keys of all reference properties.
        # Storage format of targets: models -> keys -> instance, property
        for name in set(references):
            property = getattr(model, name)
            is_key_reference = isinstance(property, KeyReferenceProperty)
            if is_key_reference:
                target_model = property.target_model
            else:
                target_model = property.reference_class
            prefetch = targets.setdefault(target_model.kind(),
                                          (target_model, {}))[1]
            for item in object_list:
                if is_key_reference:
                    # Check if we already dereferenced the property
                    if hasattr(item, '_ref_cache_for_' + property.target_name):
                        continue
                    key = getattr(item, property.target_name)
                    if property.use_key_name and key:
                        key = str(db.Key.from_path(target_model.kind(), key))
                else:
                    key = str(property.get_value_for_datastore(item))
                if key:
                    prefetch[key] = prefetch.get(key, ()) + ((item, name),)
        for target_model, prefetch in targets.values():
            prefetched_items = target_model.get(prefetch.keys())
            for prefetched, group in zip(prefetched_items, prefetch.values()):
                for item, reference in group:
                    # If prefetched is None we only update the cache
                    if not prefetched:
                        property = getattr(model, reference)
                        if isinstance(property, KeyReferenceProperty):
                            setattr(item,
                                '_ref_cache_for_' + property.target_name, None)
                        else:
                            continue
                    setattr(item, reference, prefetched)
    return object_list

class KeyReferenceProperty(object):
    """
    Creates a cached accessor for a model referenced by a string property
    that stores a str(key) or key_name. This is useful if you need to work with
    the key of a referenced object, but mustn't get() it from the datastore.

    You can also integrate properties of the referenced model into the
    referencing model, so you don't need to dereference the model within a
    transaction. Note that if the referenced model's properties change you
    won't be notified, automatically.
    """
    def __init__(self, property, model, use_key_name=True, integrate={}):
        if isinstance(property, basestring):
            self.target_name = property
        else:
            # Monkey-patch the target property, so we can monkey-patch the
            # model class, so we can detect when the user wants to set our
            # KeyReferenceProperty via the model constructor.
            # What an ugly hack; but this is the simplest implementation. :(
            # One alternative would be to implement a proxy model that
            # provides direct access to the key, but this won't work with
            # isinstance(). Maybe that's an option for Python 3000.
            # Yet another alternative would be to force the user to choose
            # either .key_name or .reference manually. That's rather ugly, too.
            self.target_name = None
            myself = self
            old_config = property.__property_config__
            def __property_config__(model_class, property_name):
                myself.target_name = property_name
                my_name = None
                for key, value in model_class.__dict__.items():
                    if value is myself:
                        my_name = key
                        break
                old_init = model_class.__init__
                def __init__(self, *args, **kwargs):
                    if my_name in kwargs:
                        setattr(self, my_name, kwargs[my_name])
                        kwargs[property_name] = getattr(self, property_name)
                        for destination, source in myself.integrate.items():
                            integrate_value = None
                            if kwargs[my_name]:
                                integrate_value = getattr_by_path(
                                    kwargs[my_name], source)
                            kwargs[destination] = integrate_value
                    old_init(self, *args, **kwargs)
                model_class.__init__ = __init__
                old_config(model_class, property_name)
            property.__property_config__ = __property_config__
        self.target_model = model
        self.use_key_name = use_key_name
        self.integrate = integrate

    def __get__(self, instance, unused):
        if instance is None:
            return self
        attr = getattr(instance, self.target_name)
        cache = getattr(instance, '_ref_cache_for_' + self.target_name, None)
        if not cache:
            cache_key = cache
        elif self.use_key_name:
            cache_key = cache.key().name()
        else:
            cache_key = str(cache.key())
        if attr != cache_key:
            if self.use_key_name:
                cache = self.target_model.get_by_key_name(attr)
            else:
                cache = self.target_model.get(attr)
            setattr(instance, '_ref_cache_for_' + self.target_name, cache)
        return cache

    def __set__(self, instance, value):
        if value and not isinstance(value, db.Model):
            raise ValueError('You must supply a Model instance.')
        if not value:
            key = None
        elif self.use_key_name:
            key = value.key().name()
        else:
            key = str(value.key())
        setattr(instance, '_ref_cache_for_' + self.target_name, value)
        setattr(instance, self.target_name, key)

        for destination, source in self.integrate.items():
            integrate_value = None
            if value:
                integrate_value = getattr_by_path(value, source)
            setattr(instance, destination, integrate_value)

def to_json_data(model_instance, property_list):
    """
    Converts a models into dicts for use with JSONResponse.

    You can either pass a single model instance and get a single dict
    or a list of models and get a list of dicts.

    For security reasons only the properties in the property_list will get
    added. If the value of the property has a json_data function its result
    will be added, instead.
    """
    if hasattr(model_instance, '__iter__'):
        return [to_json_data(item) for item in model_instance]
    json_data = {}
    for property in property_list:
        value = getattr_by_path(model_instance, property, None)
        value = getattr_by_path(value, 'json_data', value)
        json_data[property] = value
    return json_data
