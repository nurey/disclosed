#!/usr/bin/env python
# encoding: utf-8
"""
delete.py

Created by Ilia Lobsanov on 2008-04-13.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

from google.appengine.ext import db

class Contract(db.Model):
	agency_name = db.StringProperty()
	vendor_name = db.StringProperty()
	reference_number = db.StringProperty()
	contract_date = db.StringProperty()
	description = db.StringProperty()
	contract_period = db.StringProperty()
	delivery_date = db.StringProperty()
	contract_value = db.StringProperty()
	comments = db.StringProperty()


def main():
	# db.delete() requires that all entities in one call be of the same
	# entity group, because all of the deletes happen in one transaction.
	q = db.GqlQuery("SELECT * FROM Contract")
	results = q.fetch(limit=100000) # fetch all
	db.delete(results)

if __name__ == '__main__':
	main()

