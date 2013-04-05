'''
James D. Zoll

4/5/2013

Purpose: Defines metadata for the Leap Day application.

License: This is a public work.

'''

# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'Leap Day Recipedia',
            'icon': 'leapday/img/logo.png',
            'description': 'A small gaming company called Spryfox has produced a fantastic little free to play game called Leap Day. A cooperative puzzle game, players must use surrounding resources to produce ever more complicated goods in the hopes of satisfying evil spirits.',
            'button_label': 'Leap On Over',
            'default_view': 'leapday.views.index',
            'display_priority': 85,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('jQuery','http://jquery.com/'),]}