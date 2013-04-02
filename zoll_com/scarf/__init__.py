# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'Temperature Scarf',
            'icon': 'scarf/img/ravelry.png',
            'description': 'When my wife read about a fascinating knitting project on Ravelry, I thought I could help out. Called "My Year in Temperatures", the goal is to knit a scarf reflecting the temperature each day of the year. Here, users can choose their colors and location and do just that.',
            'button_label': 'Ready, Set, Knit!',
            'default_view': 'scarf.views.index',
            'display_priority': 100,
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('Bootstrap Modal', 'https://github.com/jschr/bootstrap-modal'),
                     ('jQuery','http://jquery.com/'),
                     ('jquery.cookie','https://github.com/carhartl/jquery-cookie'),
                     ('Farbtastic','http://acko.net/blog/farbtastic-jquery-color-picker-plug-in/')]}