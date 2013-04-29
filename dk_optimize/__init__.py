'''
James D. Zoll

4/29/2013

Purpose: Defines metadata for the DK Optimize application.

License: This is a public work.

'''

# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'DK Optimize',
            'icon': 'dk_optimize/img/dk_optimize.png',
            'description': 'In the popular game World of Warcraft, players are faced with many choices in how to best configure their character. In 2009, I wrote this Visual Basic application to find the best possible choices when given detailed constraints unique to each player.',
            'description_short': 'A tool for World of Warcraft enabling players to determine the best possible way to set up their character, given a specific set of constraints.',
            'button_label': 'View Project',
            'default_view': 'dk_optimize.views.index',
            'display_priority': 50,
            'uses': [('Visual Basic.NET','http://msdn.microsoft.com/en-us/vstudio/hh388573.aspx')]}