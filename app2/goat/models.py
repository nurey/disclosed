from google.appengine.ext import db, search
import re

class Contract(search.SearchableModel):
    uri = db.StringProperty()
    agency_name = db.StringProperty()
    vendor_name = db.StringProperty()
    reference_number = db.StringProperty()
    contract_date = db.StringProperty()
    description = db.StringProperty()
    contract_period = db.StringProperty()
    delivery_date = db.StringProperty()
    contract_value = db.FloatProperty()
    comments = db.TextProperty()
    import_date = db.DateTimeProperty(auto_now_add=True)
    # in version 106, we changed contract_value from StringProperty to FloatProperty.
    # let's migrate, thanks to http://kupuguy.blogspot.com/2008/05/migrating-models.html
    def __init__(self, parent=None, key=None, _app=None, contract_value=None, **kwds):
        if contract_value is not None and type(contract_value) is not float: 
            # remove anything but a dot or number
            contract_value = re.sub('[^\d\.]', '', contract_value)
            contract_value = re.sub('\.$', '', contract_value)
            #contract_value = contract_value.replace('$','').replace(',','')
            contract_value = float(contract_value or 0)
        super(Contract,self).__init__(parent, key, _app, contract_value = contract_value, **kwds)
  
class Agency(db.Model):
	name = db.StringProperty()
	contract_count = db.IntegerProperty(default=0)
	contract_value = db.FloatProperty(default=0.00)

class Vendor(db.Model):
	name = db.StringProperty()
	contract_count = db.IntegerProperty(default=0)
	contract_value = db.FloatProperty(default=0.00)
	