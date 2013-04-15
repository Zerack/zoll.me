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
            'description': 'Have you ever had trouble sending an email attachment that was too large? I created this project to let me quickly and easily share files of any size or type with family and coworkers. Login is required to view non-public files or to upload new files.',
            'description_short': 'I designed this project to quickly and easily share files with family and coworkers. Users can upload public files, or choose to make them private.',
            'button_label': 'Files This Way',
            'default_view': 'files.views.index',
            'display_priority': 90,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('Jasny Bootstrap','http://jasny.github.com/bootstrap/'),
                     ('jQuery','http://jquery.com/'),]}