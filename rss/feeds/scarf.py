'''
James D. Zoll

4/1/2013

Purpose: Defines the El Goonish Shive feed

License: This is a public work.

'''
# System Imports
import datetime

# Library Imports
import PyRSS2Gen
from django.core.urlresolvers import reverse

# Local Imports
from rss.models import Scarf_Item
from rss.feeds.Feed import Feed

# Constants
FEED_NAME = 'scarf'
FEED_LABEL = 'My Year In Temperatures'
FEED_DESC = 'A feed detailing new temperature data availability when it is published by Dayton University.'
FEED_PRIORITY = 80

RSS_TITLE = 'My Year In Temperatures Updates'
RSS_DESC = 'Status updates concerning available data for My Year In Temperatures'
RSS_ENTRY_TITLE = 'My Year In Temperatures - Data Through {0}'
RSS_ENTRY_DESC = 'New data is available for the My Year In Temperatures application! The most recent date with data is {0}.'
NUM_ENTRIES = 5

class Scarf_Feed(Feed):
    '''
    Class for the feed showing updates to available
    temperature data. This data is populated via cronjob,
    so all we have to do here is check the DB for the most
    recent entries.
    
    ''' 
    
    def __init__(self):
        '''
        Initialization of class. Passes module constants
        for feed information to the parent constructor.
        
        '''
        
        super(Scarf_Feed, self).__init__(FEED_NAME, 
                                         FEED_LABEL,
                                         FEED_DESC,
                                         FEED_PRIORITY)
    
    def fetch(self):
        '''
        The function that does the heavy lifting. Since the database 
        is populated by other sources, all we do is grab the X most
        recent entries and format them. Simple stuff.
        
        '''

        # This is quite an easy feed. For each of the 5 most recent updates, we
        # generate a feed entry.
        rss_feed_items = []
        for entry in Scarf_Item.objects.order_by('-pub_date')[:NUM_ENTRIES]:
            rss_feed_items.append(PyRSS2Gen.RSSItem(title = RSS_ENTRY_TITLE.format(datetime.datetime.strftime(entry.max_data_date, '%B %d, %Y')),
                                                    link = reverse('scarf.views.index'),
                                                    description = RSS_ENTRY_DESC.format(datetime.datetime.strftime(entry.max_data_date, '%B %d, %Y')),
                                                    guid = PyRSS2Gen.Guid(reverse('scarf.views.index')),
                                                    pubDate = entry.pub_date))
        
        # Construct the final rss feed object and return the text version.
        rss_feed = PyRSS2Gen.RSS2(title = RSS_TITLE,
                                  link = reverse('scarf.views.index'),
                                  description = RSS_DESC,
                                  lastBuildDate = datetime.datetime.now(),
                                  items = rss_feed_items
                                  )    
        return rss_feed.to_xml()

# Instantiate a feed object for the package to use.
feed = Scarf_Feed()