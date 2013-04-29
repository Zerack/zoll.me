'''
Created on Apr 22, 2013

@author: Jim
'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('dk_optimize.views',
                       url(r'^$', 'index'),    
                       )