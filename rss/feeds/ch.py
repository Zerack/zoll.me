'''
James D. Zoll

4/1/2013

Purpose: Defines the Cyanide & Happiness feed.

License: This is a public work.

'''

# System Imports
import re
import datetime
import urllib

# Library Imports
from bs4 import BeautifulSoup
import PyRSS2Gen
from django.core.urlresolvers import reverse

# Local Imports
from rss.models import CH_Item
from rss.feeds.Feed import Feed

# Constants
FEED_NAME = 'ch'
FEED_LABEL = 'Cyanide & Happiness'
FEED_DESC = 'The webcomic from explosm.net, updated to include comic images directly in the RSS feed.'
FEED_PRIORITY = 100

RSS_TITLE = 'Cyanide & Happiness (With Images)'
RSS_DESC = 'Daily comics from Cyanide & Happiness (With Images)'
SOURCE_URL = 'http://feeds.feedburner.com/Explosm'
ALT_STRING = u'Cyanide and Happiness, a daily webcomic'

# Compiled RE
COMIC_ENTRY_RE = re.compile(r'^http://www.explosm.net/comics/[0-9]+')

class CH_Feed(Feed):
    '''
    Class to define the Cyanide and Happiness feed. This fetches
    the daily comic and puts the image into the RSS feed, rather than
    just a link to the comic page as the default RSS feed for 
    explosm.net has.
    
    '''
    
    def __init__(self):
        '''
        Initialization of class. Passes module constants
        for feed information to the parent constructor.
        
        '''
        
        super(CH_Feed, self).__init__(FEED_NAME, 
                                      FEED_LABEL,
                                      FEED_DESC,
                                      FEED_PRIORITY)
    
    def fetch(self):
        '''
        Fetches the feed itself, including hitting the official feed for
        new entries and then searching for images on any new entries that are comics. 
        Entries already parsed are stored in the database for easy retrieval.
        
        '''
        
        # Fetch the official RSS feed, which is XML. We will parse this and rebuild it to contain
        # images.
        rss_soup = BeautifulSoup(urllib.urlopen(SOURCE_URL).read())
        
        # Iterate through the RSS feed and find all entries that are comics. We don't care about
        # any of the news or video items, so we'll ignore those.
        rss_feed_items = []
        for item in rss_soup.find_all('item'):
            if not COMIC_ENTRY_RE.match(item.link.text.strip()):
                continue
            
            # Now we know this is a comic entry. Check the database for an existing map for this link,
            # otherwise go fetch it.
            try:
                image_url = CH_Item.objects.get(comic_url=item.link.text.strip()).image_url            
            except CH_Item.DoesNotExist:
                # Since we don't know the image url for this comic, find it and add it to
                # our database.
                page_soup = BeautifulSoup(urllib.urlopen(item.link.text.strip()).read())
                try:
                    image_url = page_soup.find('img', {u'alt': ALT_STRING}).attrs[u'src'].strip()        
                    c = CH_Item(comic_url=item.link.text.strip(),image_url=image_url)
                    c.save()
                except:
                    # There is something unexpected happening. For now, fail silently.
                    continue
                
            # Now we know the image URL, so build our RSS Item.
            pub_date = datetime.datetime.strptime(item.title.text.strip(), '%m.%d.%Y')
            rss_feed_items.append(PyRSS2Gen.RSSItem(title = '{0} - Comic'.format(pub_date.strftime('%B %d, %Y')),
                                                    link = item.link.text.strip(),
                                                    description = '<img src="{0}" />'.format(image_url),
                                                    guid = PyRSS2Gen.Guid(item.link.text.strip()),
                                                    pubDate = pub_date))    
        
        # Construct the final rss feed object and return the text version.
        rss_feed = PyRSS2Gen.RSS2(title = RSS_TITLE,
                                  link = reverse('rss.views.feed', kwargs={'feed_name': FEED_NAME}),
                                  description = RSS_DESC,
                                  lastBuildDate = datetime.datetime.now(),
                                  items = rss_feed_items
                                  )
        
        return rss_feed.to_xml()

# Create the feed object that'll be imported by the main package.
feed = CH_Feed()