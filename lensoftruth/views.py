# Library Imports
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):    
    return render_to_response('lensoftruth/index.html', context_instance = RequestContext(request))

def tests(request):    
    return render_to_response('lensoftruth/tests.html', context_instance = RequestContext(request))