'''
Created on Apr 22, 2013

@author: Jim
'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('lensoftruth.views',
                       url(r'^$', 'index'),
                       url(r'^tests/$', 'tests'),    
                       )