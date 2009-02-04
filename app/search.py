#!/usr/bin/env python
# encoding: utf-8
"""
search.py

Created by Ilia Lobsanov on 2008-04-12.
Copyright (c) 2008 Nurey Networks Inc. All rights reserved.
"""

import wsgiref.handlers
import logging
import os
#import pprint
#pp = pprint.PrettyPrinter(indent=4,depth=5)

from google.appengine.ext import webapp, search, db
from google.appengine.ext.db import GqlQuery
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app



class Contract(db.Model):
  uri = db.StringProperty()
  agency_name = db.StringProperty()
  vendor_name = db.StringProperty()
  reference_number = db.StringProperty()
  contract_date = db.StringProperty()
  description = db.StringProperty()
  contract_period = db.StringProperty()
  delivery_date = db.StringProperty()
  contract_value = db.StringProperty()
  comments = db.TextProperty()
  
class MainPage(webapp.RequestHandler):
	def get(self):
		# We use the webapp framework to retrieve the keyword
		keyword = self.request.get('keyword')
		prop = self.request.get('prop')
		
		self.response.headers['Content-Type'] = 'text/html'
		template_values = {
		    'keyword': keyword,
		    'CURRENT_VERSION_ID': os.environ['CURRENT_VERSION_ID']
		}
		
		if keyword and prop:
		    query = Contract.all()
		    query.filter("%s =" % prop, keyword)
		    results = query.fetch(50)
		    template_values['results'] = results
		elif keyword:
			# Search the 'Contract' Entity based on our keyword
			query = search.SearchableQuery('Contract')
			query.Search(keyword)
			results = []
			results = query.Get(50)
			template_values['results'] = results
		else:
		    pass
		
		path = os.path.join(os.path.dirname(__file__), 'search_results.html')
		self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
	main()

