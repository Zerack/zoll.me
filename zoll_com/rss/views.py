'''
James D. Zoll

4/2/2013

Purpose: Defines views for the RSS application

License: This is a public work.

'''

# Library Imports
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

# Local Imports
from rss.feeds import feeds

def index(request):
    '''
    Renders the main page of the RSS application. This is just
    an index of all available feeds, shown with short descriptions.
    The feeds are ordered according to display_priority from the 
    rss.feeds feeds object.
    
    '''
    
    return render_to_response('rss/index.html', {'feeds': sorted(feeds.itervalues(), key=lambda x: x.display_priority, reverse=True)}, context_instance = RequestContext(request))

def feed(request, feed_name):
    '''
    Returns an XML feed given a specific feed name. If the
    feed does not exist, returns 404.
    
    Keyword Arguments:
    feed_name -> String. The short name of the feed to display.
    
    '''
    
    try:
        return HttpResponse(feeds[feed_name].fetch(), content_type='application/xml')
    except KeyError:
        raise Http404
    
    