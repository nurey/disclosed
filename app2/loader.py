from google.appengine.ext import bulkload
from google.appengine.api import datastore_types, datastore
from google.appengine.ext import search, db
import datetime
import logging
import time

logging.getLogger().setLevel(logging.DEBUG)

from goat.models import Contract, Agency, Vendor
	
class ContractLoader(bulkload.Loader):
    def __init__(self):
        bulkload.Loader.__init__(self, 'Contract',
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
                          ('comments', datastore_types.Text),
                          ])
  
    def HandleEntity(self, entity):
        # remove old entity
        old_key_name = entity['agency_name']+entity['reference_number']
        old_contract = Contract.get_by_key_name(old_key_name)
        
        def delete_contract(key):
            obj = db.get(key)
            obj.delete()
            
        if old_contract:
            logging.debug('attempting to delete old contract with key_name '+old_key_name)
            db.run_in_transaction(delete_contract, old_contract.key())
            
        # setup a unique key for the entity. composed of agency_name + reference_number + contract_date
        # reference number can be empty, so add contract_date
        key_name = entity['agency_name']+entity['reference_number']+(entity['contract_date'] or 'foo')
        contract = Contract.get_by_key_name(key_name)
        contract_exists = contract is not None
        # if not contract_exists:
        #     logging.debug('found a new contract with reference number:'+entity['reference_number'])

        newent = datastore.Entity('Contract', name=key_name)
        newent.update(entity)
        newent = search.SearchableEntity(newent)
        #XXX setup a parent for the entity?
        
        def increment_aggregates(key, count, value):
            obj = db.get(key)
            obj.contract_count += count
            obj.contract_value += float(value)
            obj.put()
            
        if not contract_exists:
            # increment counter for the Agency 
            agency = Agency.get_or_insert(entity['agency_name'], name=entity['agency_name'])
            db.run_in_transaction(increment_aggregates, agency.key(), 1, entity['contract_value'])
        
            # increment counter for the Vendor.
            # prepend a string to avoid BadArgumentError: Names may not begin with a digit; received 1414421 Ontario Inc
            vendor_name = 'vendor '+entity['vendor_name'] 
            vendor = Vendor.get_or_insert(vendor_name, name=vendor_name)
            db.run_in_transaction(increment_aggregates, vendor.key(), 1, entity['contract_value'])
            
        time.sleep(0.5)
        
        return newent

if __name__ == '__main__':
    bulkload.main(ContractLoader())
