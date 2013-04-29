'''
James D. Zoll

4/29/2013

Purpose: Defines the single view for the DK Optimize project.

License: This is a public work.
'''

# Library Imports
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):    
    return render_to_response('dk_optimize/index.html', context_instance = RequestContext(request))