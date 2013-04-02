'''
James D. Zoll

3/22/2013

Purpose: Defines application constants and configuration for the XBMC Photos application

License: This is a public work.

'''

from math import floor

# Constants for website presentation
PAGINATION_BUFFER = 3
IMAGES_PER_PAGE = 30

# Constants for image processing
DESIRED_RES_HORIZ = 1920
DESIRED_RES_VERT = 1080
DESIRED_ASPECT_RATIO = float(DESIRED_RES_HORIZ) / float(DESIRED_RES_VERT)
MIN_RES_VERT = 1080.0 / 2.0
MIN_RES_HORIZ = floor(MIN_RES_VERT * DESIRED_ASPECT_RATIO)
THUMBNAIL_RES_HORIZ = 700
THUMBNAIL_RES_VERT = int(floor(THUMBNAIL_RES_HORIZ * (1.0 / DESIRED_ASPECT_RATIO)))

# Index page carousel text and headings.
CAROUSEL = [('See All Photos', 'Every photo in our collection is available to browse. Click to View Photos link to the left to get started.'),
            ('Edit Photos', 'Need to re-caption or re-crop a photograph? No problem! Use the Edit Photos link in the navigation area.'),
            ('Upload Photos', 'We\'re always looking for new photos. Login to upload, title, and crop your very own photos for our screensaver.')]