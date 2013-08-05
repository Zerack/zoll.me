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
                       url(r'^$', 'index', {'hash': ''}),             
                       url(r'^(?P<hash>([a-zA-Z0-9]{2}[1-9a-u])+)/$', 'index'), # Hash counting is 0-9, then a-z, then A-Z. So, a is 10, 30 is u
                       url(r'^(?P<key>((good)|(goodtype))_[a-z]+)$', 'good', {'hash': ''}),                       
                       url(r'^(?P<hash>([a-zA-Z0-9]{2}[1-9a-u])+)/(?P<key>((good)|(goodtype))_[a-z]+)$', 'good'),
                       )