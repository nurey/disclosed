from google.appengine.ext import db
from search.core import SearchIndexProperty, porter_stemmer

class Contract(db.Model):
    uri = db.StringProperty(required=True)
    agency_name = db.StringProperty(required=True)
    vendor_name = db.StringProperty(required=True)
    reference_number = db.StringProperty(required=True)
    contract_date = db.StringProperty()
    description = db.StringProperty()
    contract_period = db.StringProperty()
    delivery_date = db.StringProperty()
    contract_value = db.FloatProperty()
    comments = db.TextProperty()
    # index used to retrieve posts
    search_index = SearchIndexProperty(('agency_name', 'vendor_name', 'description', 'comments'), indexer=porter_stemmer)

class Agency(db.Model):
	name = db.StringProperty()
	contract_count = db.IntegerProperty(default=0)
	contract_value = db.FloatProperty(default=0.00)

class Vendor(db.Model):
	name = db.StringProperty()
	contract_count = db.IntegerProperty(default=0)
	contract_value = db.FloatProperty(default=0.00)
	