# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'XBMC Photos',
            'icon': 'xbmc_photos/img/xbmc_logo.png',
            'description': 'XBMC is a fantastic piece of home media software, and we use it to display a TV slideshow of family photos in our living room. I designed this project to make it easier for all of our family members to upload and edit new photos. New photos join our slideshow nightly!',
            'description_short': 'Users can upload photos, and give each new photo a title and description. Each night, new photos are added to our TV slideshow.',
            'button_label': 'View Pictures',
            'default_view': 'xbmc_photos.views.index',
            'display_priority': 90,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Python Imaging Library','http://www.pythonware.com/products/pil/'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('Jasny Bootstrap','http://jasny.github.com/bootstrap/'),
                     ('jQuery','http://jquery.com/'),
                     ('imgAreaSelect','http://odyniec.net/projects/imgareaselect/')]}