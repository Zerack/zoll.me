'''
James D. Zoll

3/22/2013

Purpose: Defines helpers to the view functions. These are not strictly views
         since they don't have urls, but they do many of the same things.

License: This is a public work.

'''

# System Imports
from math import ceil

# Library Imports
from django.core.urlresolvers import reverse

# Local Imports
from constants import IMAGES_PER_PAGE, PAGINATION_BUFFER
from models import Photo

def get_td_all(request, role, page=1):
    ''' 
    Generates a template dictionary (template context object)
    for use in the view_all / edit_all views, with switches
    based on which photos need to be shown eventually.
    
    Keyword Arguments:
    request -> Django request. The request being served.
    role -> String. 'view' or 'edit'.
    page -> Integer. The current page of results being viewed.
    
    '''
    
    # Template context object.
    td = {'active_nav': role}
    
    # The template has a switch to show / hide some text based on the role.
    td['role'] = role
    
    # Fetch the total number of images from the database. If we're in VIEW, this is
    # all images. If we're in EDIT, this is images owned by the current user.
    num_photos = Photo.objects
    if role == 'edit':
        num_photos = num_photos.filter(user=request.user)
    elif not request.user.is_authenticated() or not request.user.has_perm('xbmc_photos.add_photo'):
        num_photos = num_photos.filter(public=True)
        
    num_photos = num_photos.count()
    num_pages = max(1,ceil(num_photos / float(IMAGES_PER_PAGE)))
    
    # Determine the current page.
    page = int(min(num_pages,max(1,int(page))))
        
    # Fetch the correct images to display on the page, using slice notation based on the current page.
    if num_photos > 0:
        td['photos'] = Photo.objects.order_by('-date')
        if role == 'edit':
            td['photos'] = td['photos'].filter(user=request.user)
        td['photos'] = td['photos'].order_by('-date')[IMAGES_PER_PAGE * (page - 1): min(IMAGES_PER_PAGE * page, num_photos)]
    else:
        td['photos'] = []
        
    # Build the object that will be passed to the pagination snippet. We need to provide
    # and ordered list of (label, href, state). Where state can be active / disabled / None
    td['pagination'] = []
    td['pagination'].append(('Prev', reverse('xbmc_photos.views.{0}_all'.format(role),args=(page-1,)) if page > 1 else None, 'disabled' if page == 1 else None))
    
    start_page = page - PAGINATION_BUFFER
    end_page = page + PAGINATION_BUFFER
    
    while start_page < 1:
        start_page += 1
        end_page = int(min(end_page + 1, num_pages))
        
    while end_page > num_pages:
        end_page -= 1
        start_page = int(max(start_page - 1, 1))
    
    for idx in range(start_page, end_page + 1):
        td['pagination'].append((idx, reverse('xbmc_photos.views.{0}_all'.format(role),args=(idx,)) if idx != page else '#', 'active' if idx == page else None))
    
    td['pagination'].append(('Next', reverse('xbmc_photos.views.{0}_all'.format(role),args=(page+1,)) if page < num_pages else None, 'disabled' if page == num_pages else None))
    
    # Everything has been constructed, so return the context
    return td