'''
James D. Zoll

4/2/2013

Purpose: Defines metadata for the rss application.

License: This is a public work.

'''

# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'RSS Feeds',
            'icon': 'rss/img/rss.png',
            'description': 'Do you ever get frustrated when the RSS feed for a site you enjoy isn\'t quite right, or just doesn\'t exist? This began as a project to enhance the RSS feed for a popular webcomic, but has grown into several customized feeds for a variety of sites.',
            'description_short': 'A collection of customized RSS feeds, covering a variety of topics. Some are new, and some modify existing RSS feeds that weren\'t quite what I wanted.',
            'button_label': 'Feed Me',
            'default_view': 'rss.views.index',
            'display_priority': 70,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap', 'http://twitter.github.com/bootstrap/'),
                     ('PyRSS2Gen','http://jquery.com/')]}