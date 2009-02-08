"""URL mappings."""

# NOTE: Must import *, since Django looks for things here, e.g. handler500.
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'goat.views',
    (r'^$', 'search_by_keyword'),
    (r'^rpc$', 'rpc_search_by_keyword'),
    (r'^adbar$', 'adbar'),
    (r'^tagcloud$', 'tagcloud'),
    (r'^chart/(.+?)/(.*)$', 'chart'),
    url(r'^search/(.+?)/(.*)$', 'search_by_prop', name='search_by_prop'),
    url(r'^contract/(.+?)/$', 'view_contract'),
    )
