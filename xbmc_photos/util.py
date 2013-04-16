'''
James D. Zoll

3/22/2013

Purpose: Defines non-view utility functions for the XBMC Photos application, such as
         a file storage path factory and a way to get the default crop box on a photograph.

License: This is a public work.

'''

# System Imports
import hashlib
import os
import datetime
from math import floor

# Local Imports
from constants import DESIRED_ASPECT_RATIO

def get_media_path_factory(basepath, attr):
    ''' 
    Returns a lambda expression that will generate
    upload filenames. This allows us to hash filenames on their
    content while only writing this once. 
    
    Keyword Argument:
    basepath -> String representing base from MEDIA_ROOT. Can contain
                strftime syntax.
                
    '''
    
    def get_media_path(basepath, attr, instance, filename):
        field_file = getattr(instance, attr)
        field_file.open()
        file_hash = hashlib.md5(field_file.read()).hexdigest()
        field_file.close()
        return os.path.join(datetime.datetime.now().strftime(basepath), file_hash + os.path.splitext(filename)[1])
    
    return lambda x, y: get_media_path(basepath, attr, x, y)
    
def get_default_crop_box(w,h):
    '''
    Returns the default crop box (left, upper, right, lower) given
    and image of WxH pixels. This is simply the largest, centered box
    of the desired aspect ratio available.
    
    Keyword Arguments:
    w -> Integer. Width of the image. Required.
    h -> Integer. Height of the image. Required.
    
    '''
    
    aspect_ratio = float(w) / float(h)
    if aspect_ratio > DESIRED_ASPECT_RATIO:
        # The image is wider than necessary, so we will provide
        # a crop box that cuts off the sides.
        top = 0
        bottom = h
        crop_width = h * DESIRED_ASPECT_RATIO
        left = int(floor((w / 2.0) - (crop_width / 2.0)))
        right = int(floor((w / 2.0) + (crop_width / 2.0)))
    else:
        # The image is taller than it can be, so we will crop out
        # the top and bottom
        left = 0
        right = w
        crop_height = w * (1 / DESIRED_ASPECT_RATIO)
        top = int(floor((h / 2.0) - (crop_height / 2.0)))
        bottom = int(floor((h / 2.0) + (crop_height / 2.0)))

    return (left, top, right, bottom)