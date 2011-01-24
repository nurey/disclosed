# Force sys.path to have our own directory first, so we can import from it.
import sys
sys.path.insert(0, '/Volumes/Devel/disclosed/app2')

from common.appenginepatch import main
from google.appengine.tools import bulkloader
from google.appengine.api import datastore_types, datastore
from google.appengine.ext import search, db
import datetime
import logging
import time

logging.getLogger().setLevel(logging.DEBUG)

from goat.models import Contract, Agency, Vendor

class ContractLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Contract',
                         [
                          ('uri', str),
                          ('agency_name', str),
						  ('vendor_name', str),
                          ('reference_number', str),
                          ('contract_date', str), #lambda x: datetime.datetime.strptime(x, "%Y-%m-%d")),
                          ('description', str),
                          ('contract_period', str),
                          ('delivery_date', str), #lambda x: datetime.datetime.strptime(x, "%Y-%m-%d") if x),
                          ('contract_value', lambda x: float(x or 0)),
                          ('comments', datastore_types.Text)
                          ])
  
    def generate_key(self, i, values):
        return values[1] + values[3] + (values[4] or 'foo')
        
loaders = [ContractLoader]
