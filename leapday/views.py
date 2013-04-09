'''
James D. Zoll
4/5/2013

Purpose: Defines application views for the Leap Day recipedia application.

License: This is a public work.

'''

# Library Imports
from django.shortcuts import render_to_response
from django.template import RequestContext

# Local Imports
from leapday.models import Good

def index(request):
    goods = Good.objects.filter(num_ingredients__lte=5).exclude(key='good_other').order_by('-value').all()
    return render_to_response('leapday/index.html', {'goods': goods}, context_instance = RequestContext(request))