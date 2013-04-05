'''
James D. Zoll
4/5/2013

Purpose: Defines application views for the Leap Day recipedia application.

License: This is a public work.

'''

# Library Imports
from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('leapday/index.html', context_instance = RequestContext(request))