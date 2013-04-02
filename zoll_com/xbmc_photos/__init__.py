# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'XBMC Photos',
            'icon': 'xbmc_photos/img/xbmc_logo.png',
            'description': 'The home media center software XBMC is a fantastic program, and we\'ve long been using the slideshow screensaver to show family photos when not watching media. I built this app to more easily format, view, and distribute all of our photographs.',
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