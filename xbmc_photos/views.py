'''
James D. Zoll

3/22/2013

Purpose: Defines all of the views for the XBMC Photos application.

License: This is a public work.

'''

# System Imports
from datetime import datetime
import StringIO
import zipfile
from os.path import join, splitext
from os import remove

# Library Imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
from PIL import Image

# Local Imports
from xbmc_photos.models import Photo
from xbmc_photos.constants import MIN_RES_HORIZ, MIN_RES_VERT, THUMBNAIL_RES_HORIZ, THUMBNAIL_RES_VERT, DESIRED_RES_HORIZ, DESIRED_RES_VERT, CAROUSEL
from xbmc_photos.util import get_default_crop_box
from xbmc_photos.view_helpers import get_td_all

def index(request):
    '''
    Displays the home / index page of the XBMC photos application. 
    This includes the main links, the carousel with application
    information, and the 6 most recently posted images, linked
    to their respective "view" pages.
    
    '''
    
    # Template object we'll pass to the renderer. td = template_dict
    td = {'active_nav': 'home'}
    
    # Some photos can be marked private and are not visible to others. While they are really
    # only hidden behind a hashed filename, this is sufficient for this application.
    if request.user.is_authenticated() and request.user.has_perm('xbmc_photos.add_photo'):
        photos = Photo.objects.order_by('?')
        recent_photos = Photo.objects.order_by('-date')[:6]
    else:
        photos = Photo.objects.filter(public=True).order_by('?')
        recent_photos = Photo.objects.filter(public=True).order_by('-date')[:6]
    
    # Build the carousel information. For each entry, we need to know the image name,
    # the header, and caption.
    td['carousel'] = [(photo, CAROUSEL[idx][0], CAROUSEL[idx][1]) for idx, photo in enumerate(photos[:len(CAROUSEL)])]
    
    # Build the list of recent photographs. This will always be the most recent six photos.
    td['recents'] = recent_photos
    
    # Ready to render the template.
    return render_to_response('xbmc_photos/index.html', td, context_instance = RequestContext(request))

def view(request, photo_id):
    ''' 
    Renders a page with detailed view information about a single photo, with id "id". Note that Edit
    links on this page are only shown if the user is logged in and has permission to edit this photograph.
    
    Keyword Arguments:
    photo_id -> String. Must match '\d+'. The ID of the photo to view.
    
    '''
    
    # Template context object
    td = {'active_nav': 'view'}
    
    is_contributor = request.user.is_authenticated() and request.user.has_perm('xbmc_photos.add_photo')
    
    # Information needed by the template.
    try:
        td['photo'] = Photo.objects.get(id=photo_id)
        
        # If the current user is authenticated AND is the owner of the photo in question
        # AND has the xbmc_photos.change_photo permission, display the edit links.
        if request.user.is_authenticated() and td['photo'].user == request.user and request.user.has_perm('xbmc_photos.change_photo'):
            td['show_edit'] = True
        
    except Photo.DoesNotExist:
        # An invalid ID was given. Replace all photo view content with an error message.
        td['invalid_id'] = True
    
    # The photo was found. If the photo is private and the user does not have xbmc_photos.add_photo
    # we raise a 404.
    if 'invalid_id' not in td and td['photo'].public == False and not is_contributor:
        raise Http404
     
    # Now, determine where the PREV and NEXT links should go. We just need the IDs of the 
    # previously and next uploaded file. In the case of the first / last image, we loop.
    if 'invalid_id' not in td:
        try:
            td['next_photo'] = Photo.objects.filter(date__gt=td['photo'].date)
            if not is_contributor:
                td['next_photo'] = td['next_photo'].filter(public=True)
            td['next_photo'] = td['next_photo'].order_by('date').all()[0]
        except IndexError:
            try:
                td['next_photo'] = Photo.objects.order_by('date')
                if not is_contributor:
                    td['next_photo'] = td['next_photo'].filter(public=True)
                td['next_photo'] = td['next_photo'].all()[0]
            except IndexError:
                td['next_photo'] = None
                
        try:
            td['prev_photo'] = Photo.objects.filter(date__lt=td['photo'].date)
            if not is_contributor:
                td['prev_photo'] = td['prev_photo'].filter(public=True)
            td['prev_photo'] = td['prev_photo'].order_by('-date').all()[0]
        except IndexError:
            try:
                td['prev_photo'] = Photo.objects.order_by('-date')
                if not is_contributor:
                    td['prev_photo'] = td['prev_photo'].filter(public=True)
                td['prev_photo'] = td['prev_photo'].all()[0]
            except IndexError:
                td['prev_photo'] = None
    
    return render_to_response('xbmc_photos/view.html', td, context_instance = RequestContext(request))

@permission_required('xbmc_photos.change_photo')
def edit(request, photo_id):
    '''
    On GET, renders a page allowing the user to edit the photograph. On POST, performs the edit
    and returns the page, flashing a message about a successful edit to the user.
    
    Keyword Arguments:
    photo_id -> String. Must match '\d+'. the ID of the photo to view.
    
    '''
    
    # Template context object
    td = {'active_nav': 'edit'}
    
    # Before even our POST handling, we can pull the photo
    # object into memory and make sure a valid ID was passed.
    try:
        td['photo'] = Photo.objects.get(id=photo_id)
    except Photo.DoesNotExist:
        # An invalid ID was given. Replace all photo view content with an error message.
        td['invalid_id'] = True
        return render_to_response('xbmc_photos/edit.html', td, context_instance = RequestContext(request))    
    
    # In the case of post, we will attempt the new cropping action.
    # If it succeeds, we'll flash a message to the user and re-show the
    # edit page. If it fails, we flash a failure message and still re-show
    # the edit page.
    if request.method == 'POST':
        # If the user is trying to edit a photograph, make sure they 
        # are the owner of the photograph. If not, raise forbidden since
        # there's no legitimate way to get to that state without trying
        # for it.
        if request.user != td['photo'].user:
            raise PermissionDenied
        
        # First, validate that all of the passed parameters are good. This means
        # title length is good, description length is good, and the crop window
        # is valid.
        validation_error = False
        try:
            title = request.POST['title']
            description = request.POST['description']
            photo_public = request.POST['photoPublic'].strip().lower()
            crop_x1 = int(request.POST['crop_x1'])
            crop_y1 = int(request.POST['crop_y1'])
            crop_x2 = int(request.POST['crop_x2'])
            crop_y2 = int(request.POST['crop_y2'])
            
            print crop_x1, crop_x2, crop_y1, crop_y2
            print crop_x2 - crop_x1, crop_y2 - crop_y1
            print MIN_RES_HORIZ, MIN_RES_VERT
            
            if (title == '' or len(title) > Photo._meta.get_field('title').max_length or
                description == '' or len(description) > Photo._meta.get_field('description').max_length or
                crop_x1 < 0 or crop_x2 > td['photo'].width or crop_x2 - crop_x1 < MIN_RES_HORIZ or
                crop_y1 < 0 or crop_y2 > td['photo'].height or crop_y2 - crop_y1 < MIN_RES_VERT or
                photo_public not in ['true','false']):
                print 'validation error'
                validation_error = True
                            
        except (KeyError, ValueError):
            validation_error = True
        
        if validation_error:
            td['flash'] = ('error','Error.','Some ooze just came out of the hard drive. Please try your request again.')
        else:
            # As far as we can tell, input is valid here. Now, we need to re-title, re-description, and re-crop the
            # image.            
            td['photo'].title = title
            td['photo'].description = description
            td['photo'].public = photo_public == 'true'         
            td['photo'].recrop(crop_x1, crop_y1, crop_x2, crop_y2)            
            td['photo'].save()         
            
            td['flash'] = ('success','Success.','The image was successfully edited. New title, description, and / or crops have been applied.')
    
    # Now, we just do the rest of the processing as though it was always
    # a GET request. Start by processing the 'prev' and 'page' parameters, which
    # tell links on the page how to handle the 'cancel' button, which varies
    # by where the user came from.
    try:
        prev = request.GET['prev'].lower()
        if prev not in ['view','edit']:
            prev = 'view'
        if prev == 'edit':
            try:
                page = max(1,int(request.GET['page']))
            except (KeyError, ValueError):
                page = 1
    except KeyError:
        prev = 'view'
    td['cancel_url'] = reverse('xbmc_photos.views.view',kwargs={'photo_id': photo_id}) if prev == 'view' else reverse('xbmc_photos.views.edit_all', kwargs={'page': page})
    
    # For the jquery_imgareselect plugin, we have to send a variety of information
    # about both the cropped and uncropped image, so that it can correctly relay
    # crop information to us and present correctly to the user. Most of that information
    # is available in the photo object being sent to the template, but some limits need to
    # be sent manually.
    td['min_width'] = MIN_RES_HORIZ
    td['min_height'] = MIN_RES_VERT
    
    # Everything is here, so let's render the page.
    return render_to_response('xbmc_photos/edit.html', td, context_instance = RequestContext(request))

def view_all(request, page=1):
    '''
    Renders a page to view all uploaded photos, which are sorted from most recent to oldest. Paginates
    the results, and uses the page parameter to determine which page to show.
    
    Keyword Arguments:
    page -> String, matches \d+. The page of results to show. Defaults to 1. Less
            than one will result in page 1 being returned. Too large will result in
            the last page being returned.
    
    '''
    
    return render_to_response('xbmc_photos/all.html', get_td_all(request, 'view', page), context_instance = RequestContext(request))

@permission_required('xbmc_photos.change_photo')
def edit_all(request, page=1):
    '''
    Displays a page very similar to the view all page, with the change that the images displays are ones
    owned by the currently logged in user, and clicking images goes direct to the edit page instead of the viewing page.
    
    Keyword Arguments:
    page -> String, matches \d+. The page of results to show. Defaults to 1. Less
            than one will result in page 1 being returned. Too large will result in
            the last page being returned.
            
    '''
    
    return render_to_response('xbmc_photos/all.html', get_td_all(request, 'edit', page), context_instance = RequestContext(request))

@permission_required('xbmc_photos.add_photo')
def new(request):
    ''' 
    Does one of two things, depending on whether this is a 
    GET or POST. If it is a GET, it shows the form to upload
    a new image. If it is a POST, it processes and image
    upload and shows either success or failure message.
    
    '''
    
    def breakout_return():
        ''' Exists as a DRY for early returning points in the code. '''
        return render_to_response('xbmc_photos/new.html', td, context_instance = RequestContext(request))
    
    td = {'active_nav': 'new'}
    
    if request.method == 'POST':
        # Alright, let's get and validate the form parameters. Form validation was
        # done once on client side, so any errors here are generally unexpected or
        # of the OH GOD OH GOD variety.
        try:
            title = request.POST['title'].strip()
            description = request.POST['description'].strip()
            photo_public = request.POST['photoPublic'].strip().lower()
            image = request.FILES['image']            
            
            if len(title) > Photo._meta.get_field('title').max_length:
                raise ValueError
            if len(description) > Photo._meta.get_field('description').max_length:
                raise ValueError
            if photo_public not in ['true','false']:
                raise ValueError
            else:
                photo_public = photo_public == 'true'
        except (KeyError, ValueError):
            # In this case, we had difficulty pulling information from the request, so
            # re-show the page with an error flash.
            td = {'error': True}
            return breakout_return()
            
        # Now we will verify that the upload is in fact an image. This is handled
        # by PIL - the image will fail to open if it is not in fact an image file.
        try:
            pil_image = Image.open(image)
        except:
            # Here, everything worked correctly, but we couldn't interpret the uploaded file
            # as an image.
            td['bad_image'] = True
            return breakout_return()
    
        # Now we will make sure that we have sufficient resolution. We must have at least MIN_HORIZ_RES
        # and MIN_VERT_RES pixels.
        o_w, o_h = pil_image.size
        print o_w, o_h
        if o_w < MIN_RES_HORIZ or o_h < MIN_RES_VERT:
            td['bad_res'] = True
            td['min_width'] = MIN_RES_HORIZ
            td['min_height'] = MIN_RES_VERT
            return breakout_return()
        
        # Alright, we have all of the data we need, so now we will push this image into our system.
        # We need to crop the original image with our default crop, and then make a thumbnail of the
        # cropped image.
        pil_image_cropped = pil_image.copy()
        pil_image_cropped.load()
        crop_box = get_default_crop_box(o_w, o_h)
        pil_image_cropped = pil_image_cropped.crop(crop_box)
        c_w = pil_image_cropped.size[0]
        print 'Width after cropping: {0}'.format(c_w)
        if c_w > DESIRED_RES_HORIZ:
            print 'Downsampling image to 1080p'
            pil_image_cropped = pil_image_cropped.resize((DESIRED_RES_HORIZ,DESIRED_RES_VERT), Image.ANTIALIAS)
        else:
            print 'Scaling image up to 1080p'
            pil_image_cropped = pil_image_cropped.resize((DESIRED_RES_HORIZ,DESIRED_RES_VERT), Image.BILINEAR)
        print 'Width after scaling: {0}'.format(pil_image_cropped.size[0])
        
        # The cropped image is now certain to be 1920x1080, so we can thumbnail it.
        pil_image_thumb = pil_image_cropped.copy()
        pil_image_thumb.thumbnail((THUMBNAIL_RES_HORIZ, THUMBNAIL_RES_VERT), Image.ANTIALIAS)
        
        # Re-construct the initial image as an InMemoryUploadedFile object, which is what the model wants.
        io_image = StringIO.StringIO()
        pil_image.save(io_image, format='JPEG')
        imuf_image = InMemoryUploadedFile(io_image, 'image', 'upload.jpg', 'jpeg', io_image.len, None)
        imuf_image.seek(0)
        
        # Re-construct the cropped image as an InMemoryUploadedFile object, which is what the model wants.
        io_image_cropped = StringIO.StringIO()
        pil_image_cropped.save(io_image_cropped, format='JPEG')
        imuf_image_cropped = InMemoryUploadedFile(io_image_cropped, 'image', 'upload.jpg', 'jpeg', io_image.len, None)
        imuf_image_cropped.seek(0)
        
        # Re-construct the thumbnail image as an InMemoryUploadedFile object, which is what the model wants.
        io_image_thumb = StringIO.StringIO()
        pil_image_thumb.save(io_image_thumb, format='JPEG')
        imuf_image_thumb = InMemoryUploadedFile(io_image_thumb, 'image', 'upload.jpg', 'jpeg', io_image.len, None)
        imuf_image_thumb.seek(0)
        
        # Build the Photo instance now that all of the images are ready to go.
        photo = Photo(title=title, description=description, date=datetime.now(), user=request.user,
                      crop_x = crop_box[0], crop_y=crop_box[1], crop_w=crop_box[2] - crop_box[0], crop_h=crop_box[3] - crop_box[1],
                      file_original=imuf_image, file_cropped=imuf_image_cropped, file_thumb=imuf_image_thumb, height=o_h, width=o_w,
                      edit_date = datetime.now(), public=photo_public)
        photo.save()
        
        td['success'] = True
        td['photo'] = photo

    # GET is ready, and POST (if present) has been processed. Render the template.
    return render_to_response('xbmc_photos/new.html', td, context_instance = RequestContext(request))

@permission_required('xbmc_photos.delete_photo')
def delete(request, photo_id):
    '''
    On a GET, this displays the delete confirmation page. On a POST, it will
    delete the picture and show a confirmation. Note that we must also
    make sure that the user deleting a photo actually owns it.
    
    Keyword Arguments:
    photo_id -> String. Must match \d+. The id of the picture to delete.
    
    '''
    
    td = {'active_nav': 'edit'}
    
    if request.method == 'GET':
        try:
            td['photo'] = Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist:
            td['invalid_id'] = True
    
        return render_to_response('xbmc_photos/delete.html', td, context_instance=RequestContext(request))
    elif request.method == 'POST':
        try:
            photo = Photo.objects.filter(user=request.user).get(id=photo_id)
        except Photo.DoesNotExist:
            raise PermissionDenied
        
        # Delete the three associated files on disk, and then delete the record.
        remove(join(settings.MEDIA_ROOT, photo.file_original.name))
        remove(join(settings.MEDIA_ROOT, photo.file_cropped.name))
        remove(join(settings.MEDIA_ROOT, photo.file_thumb.name))
        photo.delete()
            
        return render_to_response('xbmc_photos/delete_done.html', td, context_instance=RequestContext(request))
    
def zip_all(request):
    ''' 
    Returns a zip file with all cropped 1920 x 1080 photos
    included. For now this is done in memory, but if the number of
    users were larger, we would use TempFile and mkstemp() instead, to
    conserver RAM. Note that this doesn't do any permission checking,
    again because we just want to allow some photos to be marked private.
    They can be found here, but you'd have to look at the code to know
    that this URL exists.
    
    '''
    
    io_out = StringIO.StringIO()
    zip_out = zipfile.ZipFile(io_out, 'w')
    
    for photo in Photo.objects.all():
        zip_out.write(join(settings.MEDIA_ROOT, photo.file_cropped.name), '{0}{1}'.format(photo.id, splitext(photo.file_cropped.name)[1]))        
    zip_out.close()    
    io_out.seek(0)
    
    response = HttpResponse(io_out.read())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename=xbmc_photos.zip'
    response['Content-Length'] = io_out.tell()
    
    return response