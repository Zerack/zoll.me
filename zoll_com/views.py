'''
James D. Zoll

3/4/2013

Purpose: Defines some basic views for the main zoll_com application.

License: This is a public work.

'''

# System Imports
import importlib

# Library Imports
from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Constants
INDEX_NUM_APPS = 3

def index(request):
    td = {'active_nav':'index', 'apps_slice': '1:{0}'.format(INDEX_NUM_APPS + 1)}
    td['colors'] = ['0008e7', '3094f1','9ed0ff','0c8797','0dc2da']
    td['temperatures'] = [('30',20),('40',40),('50',60),('60',80)]
    return render_to_response('zoll_com/index.html', td, context_instance = RequestContext(request))

def resume(request):
    return render_to_response('zoll_com/resume.html', {'active_nav':'resume'}, context_instance = RequestContext(request))

def projects(request):
    '''
    Shows information about all current projects. This uses the installed_apps context processor to display
    information about all installed and active non-Django applications.
    
    '''
    
    return render_to_response('zoll_com/projects.html', {'active_nav':'projects'}, context_instance = RequestContext(request))

# Additional views to handle errors.
def error_400(request):
    td = {'header_text': 'Bad Request (400)',
          'body_text': 'The request could not be understood by the server.'}
    return render(request,'zoll_com/error.html', td, status=400)

def error_403(request):
    td = {'header_text': 'Forbidden (403)',
          'body_text': 'You do not have permission to access {0} on this server.'.format(request.path)}
    return render(request,'zoll_com/error.html', td, status=403)

def error_404(request):
    td = {'header_text': 'Page Not Found (404)',
          'body_text': 'The path {0} was not found on the server.'.format(request.path)}
    return render(request,'zoll_com/error.html', td, status=404)

def error_500(request):
    td = {'header_text': 'Internal Server Error (500)',
          'body_text': 'The server encountered an unexpected condition which prevented it from fulfilling your request.'}
    return render(request,'zoll_com/error.html', td, status=500)