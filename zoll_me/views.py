'''
James D. Zoll

3/4/2013

Purpose: Defines some basic views for the main zoll_me application.

License: This is a public work.

'''

# Library Imports
from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Local Imports
from xbmc_photos.models import Photo

# Constants
INDEX_NUM_APPS = 3

def index(request):
    td = {'active_nav':'index', 'apps_slice': '1:{0}'.format(INDEX_NUM_APPS + 1)}    
    newest_photo = Photo.objects.order_by('-date')
    if not request.user.is_authenticated() or not request.user.has_perm('xbmc_photos.add_photo'):
        newest_photo = newest_photo.filter(public=True)
    td['newest_photo'] = newest_photo.all()[0]
        
    return render_to_response('zoll_me/index.html', td, context_instance = RequestContext(request))

def resume(request):
    return render_to_response('zoll_me/resume.html', {'active_nav':'resume'}, context_instance = RequestContext(request))

def projects(request):
    '''
    Shows information about all current projects. This uses the installed_apps context processor to display
    information about all installed and active non-Django applications.
    
    '''
    
    return render_to_response('zoll_me/projects.html', {'active_nav':'projects'}, context_instance = RequestContext(request))

# Additional views to handle errors.
def error_400(request):
    td = {'header_text': 'Bad Request (400)',
          'body_text': 'The request could not be understood by the server.'}
    return render(request,'zoll_me/error.html', td, status=400)

def error_403(request):
    td = {'header_text': 'Forbidden (403)',
          'body_text': 'You do not have permission to access {0} on this server.'.format(request.path)}
    return render(request,'zoll_me/error.html', td, status=403)

def error_404(request):
    td = {'header_text': 'Page Not Found (404)',
          'body_text': 'The path {0} was not found on the server.'.format(request.path)}
    return render(request,'zoll_me/error.html', td, status=404)

def error_500(request):
    td = {'header_text': 'Internal Server Error (500)',
          'body_text': 'The server encountered an unexpected condition which prevented it from fulfilling your request.'}
    return render(request,'zoll_me/error.html', td, status=500)