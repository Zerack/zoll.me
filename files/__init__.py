'''
James D. Zoll

4/2/2013

Purpose: Defines metadata for the files application.

License: This is a public work.

'''

# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'File Upload / Download',
            'icon': 'files/img/files_logo.png',
            'description': 'Sick and tired of arbitrary size limits and the inability to send anything resembling an archive, I created this project to let me quickly and easily share files with my peers and coworkers. Login is required to view non-public files or to upload new files.',
            'button_label': 'Files This Way',
            'default_view': 'files.views.index',
            'display_priority': 80,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('Jasny Bootstrap','http://jasny.github.com/bootstrap/'),
                     ('jQuery','http://jquery.com/'),]}