'''
James D. Zoll

4/1/2013

Purpose: Defines all of the views for the Files application.

License: This is a public work.

'''

# System Imports
import os.path
from os import sep
import datetime
import re

# Library Imports
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.utils.http import urlencode

# Local Imports
from files.models import File, Group_Member, Group
from files.view_helpers import nav_group_entries
from files.constants import *
from zoll_com.views import error_400

def index(request):
    '''
    When the index is shown, we show the Welcome section, the Recent Uploads section,
    and the My Stats section. Welcome is static, the Recent Uploads section will show
    recently available files based on user and authenticated status, and the My Stats
    section show statistics if authenticated, and just a message saying 'login' if 
    you are not.
    
    '''
    
    # Template context dictionary.
    td = {'active_nav': 'home', 'nav_group_entries': nav_group_entries(request.user)}
    
    # Let's build the list of recently uploaded files available to the user. Any files that
    # are in groups the user is a member of, are public, or are private and owned by the user
    # count.
    public_group = Group.objects.filter(group='public').get()
    if request.user.is_authenticated():
        private_group = Group.objects.filter(group='private').get()
        user_groups = [x.group for x in Group_Member.objects.filter(user=request.user)]
        recent_files = File.objects.filter(Q(group__in=user_groups) | Q(group=public_group) | Q(Q(group=private_group) & Q(user=request.user)))
        td['user_groups'] = user_groups
    else:
        recent_files = File.objects.filter(group=public_group)
    td['recent_files'] = recent_files.all()[:5]
    
    # Now we will get counts of active files if the user is authenticated.
    if request.user.is_authenticated():
        td['public_count'] =  File.objects.filter(group=public_group).filter(user=request.user).count()
        td['private_count'] = File.objects.filter(group=private_group).filter(user=request.user).count()
        td['group_count'] = File.objects.filter(group__in=user_groups).filter(user=request.user).count()
    
    return render_to_response('files/index.html', td, context_instance = RequestContext(request))

def _list(request, group):
    '''
    Defines the view for the list of all available files under a given group. This includes
    hierarchical display of data in folder structures, etc. If the group is public,
    we require no permissions. Otherwise, we require either that the user is a member of
    the given group, or that the user is authenticated (to view private files).
    
    Keyword Arguments:
    group -> String. The group being displayed. Can be 'public', 'private', or an actual group.
    
    '''
    
    # Template context dictionary
    td = {'active_nav': group, 'nav_group_entries': nav_group_entries(request.user)}
    
    if group == 'public':
        # The public group requires no permissions, and returns just public files.
        files = File.objects.filter(group=Group.objects.filter(group='public').get()).all()
    else:
        # All other groups require an authenticated user, so redirect to login if we aren't 
        # currently authenticated.
        if not request.user.is_authenticated():
            return redirect('{0}?{1}'.format(reverse('zoll_com-login'),urlencode({'next':request.get_full_path()})))
        if group == 'private':
            # The private group returns files in "private" that are owned by the current user.
            files = File.objects.filter(group=Group.objects.filter(group='private').get()).filter(user=request.user).all()
        else:
            # Otherwise, return all files in the requested group, as long as the current user
            # is a member of that group. If the user is not a member of the group, show the forbidden page.
            try:
                db_group = Group.objects.filter(group=group).get()
                db_group_member = Group_Member.objects.filter(user=request.user).filter(group=db_group).get()
            except (Group.DoesNotExist, Group_Member.DoesNotExist):
                raise PermissionDenied          
            files = File.objects.filter(group=db_group).all()
            
    # Now we iterate over all files and construct the list of files for the template. First we
    # generate a list of the path objects we need to display, and then loop through and fill
    # them with the files.
    list_paths = []    
    for f in files:
        dp = os.path.normpath(f.display_path)
        if dp == os.path.normpath('.'):
            if dp not in list_paths:
                list_paths.append('.')
            continue
        while dp not in list_paths:
            list_paths.append(dp)
            dp = os.path.normpath(os.path.split(dp)[0])
    list_paths.sort()
    
    display_list = []
    for lp in list_paths:
        if lp != os.path.normpath('.'):
            lp_len = len(lp.split(sep))
            display_list.append(((lp_len - 1) * OFFSET_PX, LIST_ENTRY_DIR, lp.split(sep)[-1]))
        else:
            lp_len = 0
        for f in filter(lambda x: os.path.normpath(x.display_path) == lp, files):
            display_list.append((lp_len * OFFSET_PX, LIST_ENTRY_FILE, f))
            
    print display_list
    td['list'] = display_list
    
    # Add a little bit of decorative styling to the template.
    td['header'] = group.capitalize() if group in ['public','private'] else group
    if group == 'public':
        td['info'] = LIST_INFO_PUBLIC
    elif group == 'private':
        td['info'] = LIST_INFO_PRIVATE
    else:
        td['info'] = LIST_INFO_GROUP
        
    return render_to_response('files/list.html', td, context_instance = RequestContext(request))    

@login_required
def add(request, group):
    '''
    This method accepts GET and POST. On GET, displays the page to add a file to the appropriate
    group. On POST, validates the upload and adds the file to the group and path. In case of errors
    on POST, returns the GET page with an error message. On a successful POST, returns to the matching
    _list view.
    
    Keyword Arguments:
    group -> String. The group affected. Can be 'public', 'private', or a group string.
    
    '''
    
    # First we make sure the user has the appropriate permissions. Anyone can add public
    # or private files, but only members of groups can add files to that group. This permissions
    # check applies to both the GET and POST methods.
    try:
        db_group = Group.objects.filter(group=group).get()
    except Group.DoesNotExist:
        raise Http404
    
    if group not in ['public','private']:
        try:
            db_user_group = Group_Member.objects.filter(user=request.user).filter(group=db_group).get()
        except Group_Member.DoesNotExist:
            raise PermissionDenied
    
    # Template context dictionary
    td = {'active_nav': group, 'nav_group_entries': nav_group_entries(request.user)}
    
    if request.method == 'POST':        
        # If the request is a POST, validate the form input. In this case, it's just that the
        # file exists and that file_path is a valid filepath.
        if 'file_path' not in request.POST or 'new_file' not in request.FILES:
            return error_400(request)
        
        file_path = os.path.normpath(request.POST['file_path'].strip())
        uploaded_file = request.FILES['new_file']
        
        # Process file path. We need to do some cleaning to make sure we can get a clear
        # path from it. We don't have to worry about _security_, because the file isn't
        # written to disk using this path, just displayed.
        if file_path == os.path.normpath(''):
            cleaned_path = ''
        else:
            file_path = file_path.split(sep)
            cleaned_path = []
            for entry in file_path:
                if re.match(r'[/\\?*:|"<>.\']', entry):
                    return error_400(request)
                cleaned_entry = entry.strip()
                if cleaned_entry == '':
                    return error_400(request)               
                cleaned_path.append(cleaned_entry)
            cleaned_path = sep.join(cleaned_path)
        
        # All is well, so add the file object to the database, which will also write it do disk via
        # Django's FileField model field.
        db_file = File(uploaded_file=uploaded_file, display_path=cleaned_path, date=datetime.datetime.now(),
                       group=db_group, user=request.user)
        db_file.save()
        
        messages.add_message(request, messages.SUCCESS, 'The file "{0}" was successfully uploaded.'.format(os.path.basename(db_file.uploaded_file.name)))
        return redirect(reverse('files.views._list', kwargs={'group': group}))    
    
    # If this is a get request, we can just go ahead and return the add template.
    return render_to_response('files/add.html', td, context_instance = RequestContext(request))

def get(request, file_id):
    ''' 
    Handles a request to actually download a file. We pass
    through the Django WSGI object so that we can enforce permissions
    on the appropriate level. If we're in DEBUG, serve the file
    out of Django. If we're not in debug, we are going to use the Apache
    X-Sendfile mod to serve files.
    
    Keyword Arguments:
    file_id -> String, must match \d+. The file ID to be downloaded.
    
    '''
    
    def make_file_response():
        ''' 
        Performs the work of response syntax based on settings.DEBUG.
        In the debug environment, we just serve the file. In the production
        environment, we use Apache mod-xsendfile to securely send files using
        the Apache software instead of the django wsgi object for efficiency.
        
        '''
        
        if settings.DEBUG:
            return redirect(db_file.uploaded_file.url)
        else:
            response = HttpResponse(mimetype='application/force-download')
            response['Content-Disposition']= 'attachment; filename={0}'.format(os.path.basename(db_file.uploaded_file.name))
            response['X-Sendfile'] = os.path.join(settings.MEDIA_ROOT, db_file.uploaded_file.name)
            return response
    
    try:
        db_file = File.objects.filter(id=file_id).get()  
    except File.DoesNotExist:
        return Http404
    
    if db_file.group.group == 'public':
        # In this case, anyone is permitted to download the file.
        return make_file_response()
    
    # Since the file exists and is not public, return forbidden if the
    # user is not authenticated.
    if not request.user.is_authenticated():
        raise PermissionDenied
    
    if db_file.group.group == 'private':
        # In this case, only the owning user is permitted to download the file.
        if request.user == db_file.user:
            return make_file_response()
        else:
            raise PermissionDenied
        
    # Now we know the file is neither public nor private, so check the user's
    # groups.
    if db_file.group in [x.group for x in Group_Member.objects.filter(user=request.user).all()]:
        return make_file_response()
    else:
        raise PermissionDenied

@login_required
def delete(request, file_id):
    '''
    Shows two different pages on POST / GET. On GET, shows an 
    'Are you sure?' page to delete a file. On POST, deletes the
    file and redirects back to the appropriate listing page. All
    methods require that the requesting user is the owner of
    the file in question.
    
    Keyword Arguments:
    file_id -> String. Matches \d+. The id of the file in question.
    
    '''
    
    # First, make sure the file exists, and return 404 if it does not.
    try:
        db_file = File.objects.filter(id=file_id).get()
    except File.DoesNotExist:
        raise Http404
    
    # If the user does not own the file, throw forbidden. Otherwise, proceed.
    if db_file.user != request.user:
        raise PermissionDenied
    
    # Template context dictionary
    td = {'active_nav': db_file.group.group, 'nav_group_entries': nav_group_entries(request.user)}
    
    if request.method == 'POST':        
        deleted_file_name = os.path.basename(db_file.uploaded_file.name)
        
        # The file itself must be explicitly deleted prior to record deletion.
        db_file.uploaded_file.delete()
        db_file.delete()
        
        messages.add_message(request, messages.SUCCESS, 'The file "{0}" was successfully deleted.'.format(os.path.basename(deleted_file_name)))
        return redirect(reverse('files.views._list', kwargs={'group': db_file.group.group}))
        
    td['db_file'] = db_file
    return render_to_response('files/delete.html', td, context_instance = RequestContext(request))