import os

# AppEngine imports
#from google.appengine.api import mail
#from google.appengine.api import memcache
#from google.appengine.api import users
#from google.appengine.api import urlfetch
from google.appengine.ext import db, search
from google.appengine.ext.db import djangoforms

# Django imports
# TODO(guido): Don't import classes/functions directly.
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response
import django.template
from django.utils import simplejson

import logging
logging.getLogger().setLevel(logging.DEBUG)
    
from models import Contract, Agency, Vendor

#XXX memcache this
def contract_count():
	agencies = Agency.all().fetch(200)
	count = 0
	for agency in agencies:
	    count += agency.contract_count
	return count
	
global_template_params = {
    'contract_count': contract_count(),
    'CURRENT_VERSION_ID': os.environ['CURRENT_VERSION_ID']
}

def search_by_prop(request, prop=None, keyword=None):
    template_params = {
	    'keyword': keyword,
	    'prop': prop,
	}
    template_params.update(global_template_params)
	
    if keyword and prop:
	    query = Contract.all()
	    query.filter("%s =" % prop, keyword)
	    more_template_params = _process_query(request, query)
	    template_params.update(more_template_params)
    else:
	    pass
	    
    return render_to_response('search_results.html', template_params)
    
	    
def search_by_keyword(request):
	keyword = request.GET.get('keyword') or ''
	
	template_params = {
	    'keyword': keyword,
	    'dev': os.environ["SERVER_SOFTWARE"].find('Development') != -1
	}
	template_params.update(global_template_params)
	
	if keyword:
		# Search the 'Contract' Entity based on our keyword
		#query = search.SearchableQuery('Contract')
		#query.Search(keyword)
		#results = query.Get(50)
		query = Contract.all().search(keyword)
		more_template_params = _process_query(request, query)
		template_params.update(more_template_params)
	else:
	    pass
	
	return render_to_response('search_results.html', template_params)

def rpc_search_by_keyword(request):
    keyword = request.GET.get('keyword') or ''
    offset = int(request.GET.get('offset') or 0)
    limit = 50

    response = {
        'keyword': keyword,
        'CURRENT_VERSION_ID': os.environ['CURRENT_VERSION_ID']
    }
    if keyword:
        resultset = []
    	query = Contract.all().search(keyword)
    	results = query.fetch(limit, offset)
    	#XXX django simplejson can't understand db.Model entities yet
    	for result in results:
            result.contract_value = result.contract_value.replace('$', '')
            result.contract_value = result.contract_value.replace(',', '')
            try:
                result.contract_value = float(result.contract_value)
            except:
                # contract_value could have chars
                pass

            resultset.append({ 
                'agency_name' : result.agency_name, 
                'vendor_name' : result.vendor_name, 
                'contract_value' : result.contract_value,
                'contract_date': result.contract_date,
                'description': result.description,
                'comments': result.comments,
                'uri': result.uri,
                 })
    	response['resultset'] = resultset
    else:
        pass
	    
    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')
    
def adbar(request):
    return render_to_response('adbar.html', {})
    
def tagcloud(request):
    # get agencies sorted by contract_value
	agencies = Agency.all().order("name").fetch(200)
	return render_to_response('tagcloud.html', { 'agencies': agencies })

PAGESIZE=10

def _process_query(request, query):
    template_params = {}
    total_value = 0
    total_cnt = 0
    next = None
    results = None
    
    # implement paging as per http://code.google.com/appengine/articles/paging.html
    bookmark = request.GET.get("bookmark")
    if bookmark:
        results = query.order("-contract_date").filter('contract_date <=', bookmark).fetch(PAGESIZE+1)
    else:
        results = query.order("-contract_date").fetch(PAGESIZE+1);
    if len(results) == PAGESIZE + 1:
        next = results[-1].contract_date
    results = results[:PAGESIZE]
    template_params['contract_count'] = contract_count()
    template_params['next'] = next
    template_params['results'] = results
    template_params['total_value'] = total_value
    template_params['total_cnt'] = total_cnt
	
    return template_params