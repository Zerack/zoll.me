# Define application information here, for use by the main application in displaying
# linkbacks to the application, etc.
app_info = {'name': 'Temperature Scarf',
            'icon': 'scarf/img/ravelry.png',
            'description': 'When my wife read about a fascinating knitting project, I wanted to help out. Called "My Year in Temperatures", the goal is to knit a scarf reflecting the local temperature each day of the year. Users choose colors and a location before generating a personalized scarf pattern.',
            'button_label': 'Ready, Set, Knit!',
            'default_view': 'scarf.views.index',
            'display_priority': 100,
            'spotlight': {'template': 'scarf/spotlight.html',
                          'context': { 'colors': ['0008e7', '3094f1','9ed0ff','0c8797','0dc2da'],
                                       'colors_dark': [],
                                       'temperatures': [('30',20),('40',40),('50',60),('60',80)]},
                          'css': 'scarf/css/spotlight.css'
                          },
            'uses': [('postgreSQL','http://www.postgresql.org'),
                     ('Django','https://www.djangoproject.com'),
                     ('Bootstrap','http://twitter.github.com/bootstrap/'),
                     ('Bootstrap Modal', 'https://github.com/jschr/bootstrap-modal'),
                     ('jQuery','http://jquery.com/'),
                     ('jquery.cookie','https://github.com/carhartl/jquery-cookie'),
                     ('Farbtastic','http://acko.net/blog/farbtastic-jquery-color-picker-plug-in/')]}