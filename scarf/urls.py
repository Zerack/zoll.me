'''
James D. Zoll

1/2/2013

Purpose: Defines url rules for the main portion of the scarf application

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, url

# Setup the list views and generic views.
urlpatterns = patterns('scarf.views',
                       url(r'^$', 'index'),
                       url(r'^(?P<city>[ ()a-zA-Z0-9.]+)/(?P<year>\d{4})/(?P<temperature_config>([0-9a-fA-F]{6}-[a-zA-Z0-9 ]*)(/(-?\d+(\.\d+)?)/([0-9a-fA-F]{6}-[a-zA-Z0-9 ]*))+)$', 'index'),
                       url(r'^results/$', 'results', name='results_clean'), # Exists for the purposes of using {% url 'scarf.views.results_clean %} in a template.
                       url(r'^results/(?P<city>[ ()a-zA-Z0-9.]+)/(?P<year>\d{4})/(?P<temperature_config>([0-9a-fA-F]{6}-[a-zA-Z0-9 ]*)(/(-?\d+(\.\d+)?)/([0-9a-fA-F]{6}-[a-zA-Z0-9 ]*))+)/$', 'results')
                       )