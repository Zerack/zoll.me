'''
James D. Zoll

4/1/2013

Purpose: Defines URL rules for the Files application.

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('files.views',
                       url(r'^$', 'index'),
                       url(r'^list/(?P<group>.+)/$', '_list'),
                       url(r'^add/(?P<group>.+)/$', 'add'),
                       url(r'^get/(?P<file_id>\d+)/$', 'get'),
                       url(r'^delete/(?P<file_id>\d+)/$', 'delete'),
                       )