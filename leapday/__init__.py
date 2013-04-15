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
            'description': 'A small gaming company called Spry Fox has produced a cooperative puzzle game called Leap Day. This project catalogs recipes that players must use to craft game-winning items. Recipes are searchable and sortable, and each has detailed production information.',
            'description_short': 'This project catalogs recipes for the cooperative game Leap Day by Spry Fox. Recipes can be searched, and each has detailed production information.',
            'button_label': 'Leap On Over',
            'default_view': 'leapday.views.index',
            'display_priority': 85,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('jQuery','http://jquery.com/'),
                     ('Stupid-table-plugin', 'http://joequery.github.io/Stupid-Table-Plugin/'),
                     ('ExplorerCanvas', 'http://excanvas.sourceforge.net/')]}