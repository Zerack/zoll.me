'''
James D. Zoll

3/22/2013

Purpose: Defines URL paths for the XBMC Photos application

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('xbmc_photos.views',
                       url(r'^$', 'index'),
                       url(r'^view/(?P<photo_id>\d+)/$', 'view'),
                       url(r'^view/all/(?P<page>\d+)/$', 'view_all'),
                       url(r'^view/all/$', 'view_all'),
                       url(r'^edit/all/(?P<page>\d+)/$', 'edit_all'),
                       url(r'^edit/all/$', 'edit_all'),
                       url(r'^edit/(?P<photo_id>\d+)/$', 'edit', name='xbmc_photos.edit'),
                       url(r'^new/$', 'new'),
                       url(r'^delete/(?P<photo_id>\d+)/$', 'delete'),
                       url(r'^zip/$', 'zip_all'),
                       )