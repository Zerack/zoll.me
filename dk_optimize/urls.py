'''
James D. Zoll

4/29/2013

Purpose: Defines the single URL rule for the DK Optimize project.

License: This is a public work.
'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('dk_optimize.views',
                       url(r'^$', 'index'),    
                       )