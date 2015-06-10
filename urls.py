from django.conf.urls.defaults import *
import cybertracker_reports.views
import cybertracker_reports.biokids.catalog
import cybertracker_reports.biokids.containers
import cybertracker_reports.biokids.search
import cybertracker_reports.biokids.classification
import cybertracker_reports.biokids.nodes
import cybertracker_reports.biokids.glossary
import cybertracker_reports.cybertracker.views
from django.contrib.auth.views import login, logout

import os
from cybertracker_reports.settings import MEDIA_ROOT

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

ADMIN_MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(admin.__file__)), 'media')

urlpatterns = patterns('',
    # Example:
    # (r'^lab51/', include('cybertracker_reports.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/auth/user/(?P<id>\d+)/$', 'cybertracker_reports.admin_views.manage_user'),
    # (r'^admin/', include('django.contrib.admin.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ADMIN_MEDIA_ROOT}),

    # static routes
    (r'^$', cybertracker_reports.biokids.nodes.frontpage),
    
    (r'^login/$', cybertracker_reports.views.login),
    
    (r'^cybertracker/$', cybertracker_reports.cybertracker.views.index),
    (r'^cybertracker/choose_report/$', cybertracker_reports.cybertracker.views.choose_report),
    (r'^cybertracker/verify_upload/$', cybertracker_reports.cybertracker.views.verify_upload),
    (r'^cybertracker/process_upload/$', cybertracker_reports.cybertracker.views.process_upload),
    (r'^cybertracker/upload/$', cybertracker_reports.cybertracker.views.upload),
    (r'^cybertracker/recycle/$', cybertracker_reports.cybertracker.views.recycle),
    (r'^cybertracker/habitat_report/(?P<group_code>\d+)/$', cybertracker_reports.cybertracker.views.habitat_report),
    (r'^cybertracker/observation_report/(?P<group_code>\d+)/$', cybertracker_reports.cybertracker.views.observation_report),
    (r'^cybertracker/zone_report/(?P<group_code>\d+)/$', cybertracker_reports.cybertracker.views.zone_report),
    (r'^cybertracker/team_report/(?P<group_code>\d+)/$', cybertracker_reports.cybertracker.views.team_report),
    (r'^cybertracker/energy_role_report/(?P<group_code>\d+)/$', cybertracker_reports.cybertracker.views.energy_role_report),
    
    (r'^accounts/login/$', login, { 'template_name':'cybertracker/index.html' }),
    (r'^accounts/logout/$', logout, { 'template_name':'logged_out.html' }),
    
    (r'^critters/$', cybertracker_reports.biokids.catalog.index),
    (r'^critters/(?P<special>many_legs|no_legs)/$', cybertracker_reports.biokids.catalog.special),
    (r'^critters/featured_critter/$', cybertracker_reports.biokids.catalog.featured_critter),
    

    # critters/classification is different
    (r'^critters/(?P<scientific_name>[A-Za-z_\,\(:\)0-9]+)/classification/$', cybertracker_reports.biokids.classification.listing),
    (r'^critters/(?P<scientific_name>[A-Za-z_\,\(:\)0-9]+)/carousel/$', cybertracker_reports.biokids.catalog.carousel),

    # critters/
    (r'^critters/(?P<scientific_name>[A-Za-z][A-Za-z_,\(:\)0-9]+)/(?P<feature>\w+)/(?P<terms>[A-Za-z_\+\-]+)/(?P<p>\d+)/$', cybertracker_reports.biokids.catalog.dispatcher),
    (r'^critters/(?P<scientific_name>[A-Za-z][A-Za-z_,\(:\)0-9]+)/(?P<feature>\w+)/(?P<terms>[A-Za-z_\+\-]+)/$', cybertracker_reports.biokids.catalog.dispatcher),
    (r'^critters/(?P<scientific_name>[A-Za-z][A-Za-z_,\(:\)0-9]+)/(?P<feature>\w+)/(?P<p>\d+)/$', cybertracker_reports.biokids.catalog.dispatcher),
    (r'^critters/(?P<scientific_name>[A-Za-z][A-Za-z_\,]+)/(?P<feature>\w+)/$', cybertracker_reports.biokids.catalog.dispatcher),
    (r'^critters/(?P<scientific_name>[A-Za-z][A-Za-z_,\(:\)0-9]+)/$', cybertracker_reports.biokids.catalog.dispatcher, { 'feature' : 'information' }),

    (r'^critters/(?P<node_id>\d+)/(?P<scientific_name>[A-Za-z_,\(:\)0-9]+)/(?P<feature>\w+)/$', cybertracker_reports.biokids.catalog.show),
    (r'^critters/(?P<node_id>\d+)/(?P<scientific_name>[A-Za-z_,\(:\)0-9]+)/(?P<feature>\w+)/(?P<terms>[A-Za-z_\+\-]+)/$', cybertracker_reports.biokids.catalog.show),
    
    # collections/
    (r'^collections/redirect/$', cybertracker_reports.biokids.containers.redirect),
    (r'^collections/(?P<node_id>\d+)/in/(?P<collection_id>\d+)/$', cybertracker_reports.biokids.containers.show),
    (r'^collections/(?P<node_id>\d+)/in/(?P<collection_id>\d+)/(?P<terms>[A-Za-z_\+\-]+)/$', cybertracker_reports.biokids.containers.show),
    (r'^collections/(?P<collection_id>\d+)/carousel/$', cybertracker_reports.biokids.containers.carousel),
    (r'^collections/(?P<collection_id>\d+)/(?P<terms>[A-Za-z_\+\-]+)/(?P<page>\d+)/$', cybertracker_reports.biokids.containers.listing),
    (r'^collections/(?P<collection_id>\d+)/(?P<page>\d+)/$', cybertracker_reports.biokids.containers.listing),
    (r'^collections/(?P<collection_id>\d+)/$', cybertracker_reports.biokids.containers.listing),
    
    # search/
    (r'^search/find/$', cybertracker_reports.biokids.search.process),
    (r'^search/$', cybertracker_reports.biokids.search.query, { 'feature':'information' }),
    (r'^search/(?P<text>[\w\+\-\(\)\!]+)/$', cybertracker_reports.biokids.search.query, { 'feature':'information' }),
    (r'^search/(?P<text>[\w\+\-\(\)\!]+)/(?P<feature>\w+)/$', cybertracker_reports.biokids.search.query),
    (r'^search/(?P<text>[\w\+\-\(\)\!]+)/(?P<feature>[A-Za-z_\-]+)/(?P<page>\d+)/$', cybertracker_reports.biokids.search.query),
    
    # glossary/
    (r'^glossary/index/$', cybertracker_reports.biokids.glossary.index),
    (r'^glossary/index/(?P<initial>[a-z])/$', cybertracker_reports.biokids.glossary.index),
    (r'^glossary/popup/(?P<guid>[\w:]+)/$', cybertracker_reports.biokids.glossary.popup),
    (r'^glossary/(?P<guid>[\w:]+)/$', cybertracker_reports.biokids.glossary.show),
    
    
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Projects/junebug/lab12/public/files'}),
    (r'^via/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Projects/junebug/lab12/public/via'}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + '/public/images'}),
    (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + '/public/stylesheets'}),
    (r'^javascripts/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + '/public/javascripts'}),
    (r'^helpers/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT + '/public/helpers'}),
    
    # books/
    (r'^(?P<section>[a-z\-_]+)/$', cybertracker_reports.biokids.nodes.show),
    (r'^(?P<section>[a-z\-_]+)/(?P<args>[A-Za-z\-_0-9/]+)/$', cybertracker_reports.biokids.nodes.show),
)

handler404 = 'cybertracker_reports.views.custom_404'
handler500 = 'cybertracker_reports.views.custom_500'
