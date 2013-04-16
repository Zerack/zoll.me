'''
James D. Zoll

3/22/2013

Purpose: Defines URL paths for the Leap Day application

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('leapday.views',
                       url(r'^$', 'index'),               
                       url(r'^(?P<key>[a-zA-Z_]+)$', 'good'),
                       )