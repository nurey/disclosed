import os, math

# AppEngine imports
#from google.appengine.api import mail
from google.appengine.api import memcache
#from google.appengine.api import users
#from google.appengine.api import urlfetch
from google.appengine.ext import db, search
#from google.appengine.ext.db import djangoforms
from google.appengine.ext.db import GqlQuery

# Django imports
# TODO(guido): Don't import classes/functions directly.
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response
import django.template
from django.utils import simplejson

import traceback
import logging
logging.getLogger().setLevel(logging.DEBUG)

from models import Contract, Agency, Vendor
import utils

#XXX memcache this
def contract_count():
	agencies = Agency.all().fetch(200)
	count = 0
	for agency in agencies:
	    count += agency.contract_count
	return count

def global_template_params():
    return {
        'contract_count': contract_count(),
        'CURRENT_VERSION_ID': os.environ['CURRENT_VERSION_ID']
    }

def search_by_prop(request, prop=None, keyword=None):
    template_params = {
	    'keyword': keyword,
	    'prop': prop,
	}
    template_params.update(global_template_params())
    
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
	template_params.update(global_template_params())
	
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
	query = Agency.all().order("name")
	agencies = []
	for agency in query:
	    agency.weight = utils.tag_weight(agency.contract_value)
	    agencies.append(agency)
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

def view_contract(request, key_name):
    logging.debug("key_name="+key_name)
    result = Contract.get_by_key_name(key_name)
    template_params = {}
    template_params['result'] = result
    return render_to_response('contract.html', template_params)

def chart(request, model, fetch_limit):
    memcache_key = "chart:%s:%s" % (model, fetch_limit)
    gchart_url = memcache.get(memcache_key)
    # this method only applies to models with a contract_value attribute
    if gchart_url is None:
        # figure out the chart title based on the plural of the model name
        model_plural = {
            'Agency': 'Agencies',
            'Vendor': 'Vendors',
        }
        chart_title = "Top %s %s" % (fetch_limit, model_plural[model])
        
        try:
            #entities = model.all().order("-contract_value").fetch(fetch_limit)
            entities = GqlQuery("SELECT * FROM %s ORDER BY contract_value DESC" % model).fetch(int(fetch_limit))
        except Exception:
            logging.info(traceback.format_exc())
    	    return None
        names = []
        values = []
        for entity in entities:
    	    #names.append(agency.name + ": " + utils.currency(int(agency.contract_value)))
    	    entity_name = entity.name.replace('vendor ', '') #XXX remove this line when we fix Vendor.name
    	    names.append(entity_name)
    	    values.append(entity.contract_value)
    
        names_str = '|'.join(names)
        value_min = min(values)
        value_max = max(values)
        values_str = ','.join([str((math.ceil(value/value_max*100))) for value in values])
	
        gchart_url = "http://chart.apis.google.com/chart?chtt=%s&chs=700x350&chd=t:%s&cht=p&chl=%s" % (chart_title, values_str, names_str)
        memcache.add(memcache_key, gchart_url, 3600) #expiration: 1 hour
    return HttpResponsePermanentRedirect(gchart_url)
