'''
James D. Zoll

4/29/2013

Purpose: Defines the two required URL rules for the lensoftruth.js application.

License: This is a public work.
'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('lensoftruth.views',
                       url(r'^$', 'index'),
                       url(r'^tests/$', 'tests'),    
                       )