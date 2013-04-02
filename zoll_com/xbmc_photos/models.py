'''
James D. Zoll

3/22/2013

Purpose: Defines database models for the XBMC Photos application

License: This is a public work.

'''

# System Imports
from os.path import join
import datetime

# Library Imports
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image

# Local Imports
from util import get_media_path_factory
from constants import THUMBNAIL_RES_HORIZ, THUMBNAIL_RES_VERT, DESIRED_RES_HORIZ, DESIRED_RES_VERT

# Create your models here.
class Photo(models.Model):
    title = models.CharField(max_length=25)
    description = models.CharField(max_length=1000)
    date = models.DateTimeField()
    edit_date = models.DateTimeField()
    user = models.ForeignKey(User)
    height = models.IntegerField()
    width = models.IntegerField()
    crop_x = models.IntegerField()
    crop_y = models.IntegerField()
    crop_w = models.IntegerField()
    crop_h = models.IntegerField()
    file_original = models.ImageField(upload_to=get_media_path_factory('xbmc_photos/original/%Y/%m/%d', 'file_original'))
    file_cropped = models.ImageField(upload_to=get_media_path_factory('xbmc_photos/cropped/%Y/%m/%d', 'file_cropped'))
    file_thumb = models.ImageField(upload_to=get_media_path_factory('xbmc_photos/thumb/%Y/%m/%d', 'file_thumb'))
    
    def recrop(self, left, top, right, bottom):
        ''' 
        Applies the given crop box to the image in question, and
        then re-saves the file_cropped and file_thumb file with the
        original hash, overwriting the existing files.
        
        Keyword Arguments:
        left -> Coordinate of the left edge of the box.
        top -> Top edge
        right -> Right edge
        bottom -> Bottom edge.
        
        '''
        
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)
        print left, top, right, bottom
        
        pil_image_original = Image.open(self.file_original.file)
        pil_image_cropped = pil_image_original.copy()
        pil_image_cropped.load()
        pil_image_cropped = pil_image_cropped.crop((left,top,right,bottom))
        self.file_original.file.close()
        
        c_w = pil_image_cropped.size[0]
        if c_w > DESIRED_RES_HORIZ:
            pil_image_cropped = pil_image_cropped.resize((DESIRED_RES_HORIZ,DESIRED_RES_VERT), Image.ANTIALIAS)
        else:
            pil_image_cropped = pil_image_cropped.resize((DESIRED_RES_HORIZ,DESIRED_RES_VERT), Image.BILINEAR)
        
        pil_image_thumb = pil_image_cropped.copy()
        pil_image_thumb.thumbnail((THUMBNAIL_RES_HORIZ, THUMBNAIL_RES_VERT), Image.ANTIALIAS)
        
        pil_image_cropped.save(join(settings.MEDIA_ROOT, self.file_cropped.name))
        pil_image_thumb.save(join(settings.MEDIA_ROOT, self.file_thumb.name))
        
        self.edit_date = datetime.datetime.now()
        self.crop_x = left
        self.crop_y = top
        self.crop_w = right - left
        self.crop_h = bottom - top
        
        print 'Finished Recrop'