'''
James D. Zoll

4/5/2013

Purpose: Defines metadata for the Lens of Truth application.

License: This is a public work.

'''

# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'lensoftruth.js',
            'icon': 'lensoftruth/img/lensoftruth.png',
            'description': 'jQuery has as very powerful data api to store strings and JavaScript objects on nodes in the DOM. These attributes are not directly visible in the DOM, so they can be hard to debug. The lensoftruth.js jQuery plugin fixes that by adding visible data attributes while debugging.',
            'description_short': 'This lightweight jQuery plugin adds visible data-* attributes directly in the DOM when you call $.data(), making debugging easy in all browsers.',
            'button_label': 'Reveal The Truth',
            'default_view': 'lensoftruth.views.index',
            'display_priority': 83,
            'uses': [('jQuery','http://jquery.com/')]}