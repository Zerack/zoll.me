'''
James D. Zoll

4/2/2013

Purpose: Defines a context processor for the application that will inject information
         about all installed (non-django) applications into the request context, for
         the purpose of building the navbar menus, index, and projects page.
         
License: This is a public work

'''

# System Imports
import importlib
import re

# Library Imports
from django.conf import settings

# Constants
APP_EXCLUDE_RE = re.compile(r'^(django)|(compressor)', re.IGNORECASE)
APP_EXCLUDE_LAMBDA = lambda x: not APP_EXCLUDE_RE.match(x)
APP_SORT_LAMBDA = lambda x: -1 * x['display_priority']

# When this script is actually executed, we need to go out and grab information about each of
# the projects that we've added. This allows us to add projects without having to manually
# update these views.
_apps = []
for app_string in filter(APP_EXCLUDE_LAMBDA, settings.INSTALLED_APPS):
    t = importlib.import_module(app_string)
    try:
        _apps.append(t.app_info)
    except AttributeError:
        pass
_apps.sort(key=APP_SORT_LAMBDA)

def installed_apps(request):
    '''
    Adds the "apps" object to all requests, which will
    include information about all non-Django applications,
    sorted in descending order of importance.
    
    '''
    
    return {'apps': _apps}