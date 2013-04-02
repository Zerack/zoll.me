'''
James D. Zoll

4/2/2013

Purpose: Define a class that the various feeds can inherit from.

License: This is a public work.

'''

class Feed(object):
    ''' 
    Base class for Feeds. Do not instantiate directly.
    
    '''
    def __init__(self, name, label, description, display_priority):
        '''
        Initialization just pushes some metadata about the feed into
        instance variables. Nothing fancy.
        
        Keyword Arguments:
        name -> String. Name used for the feed URL
        label -> String. Verbose name of the feed
        description -> String. Description of the feed.
        display_priority -> Integer. Higher is higher priority.
        
        '''
        
        self.name = name
        self.label = label
        self.description = description
        self.display_priority = display_priority
        
    def fetch(self):
        '''
        The function to call that returns a string of XML representing
        the feed. Do not call on the parent class.
        
        '''
        
        pass