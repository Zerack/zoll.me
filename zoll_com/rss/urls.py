'''
James D. Zoll

4/2/2013

Purpose: Defines URL rules for the RSS application

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('rss.views',
                       url(r'^$', 'index'),
                       url(r'^feeds/(?P<feed_name>[a-z0-9_]+)/$', 'feed'),    
                       )