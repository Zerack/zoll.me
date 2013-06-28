'''
James D. Zoll

4/1/2013

Purpose: Defines the El Goonish Shive feed

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
from rss.models import EGS_Item
from rss.feeds.Feed import Feed

# Constants
FEED_NAME = 'egs'
FEED_LABEL =  'El Goonish Shive'
FEED_DESC = 'A combination of the main comic feed and the sketchbook feed, with images and commentary included.'
FEED_PRIORITY = 90

SOURCE_DOMAIN = 'http://www.egscomics.com'
SOURCE_URL_COMIC = 'http://www.egscomics.com/rss.php'
SOURCE_URL_SKETCHBOOK = 'http://www.egscomics.com/sketchbook/rss.php'
RSS_TITLE = 'El Goonish Shive (With Images)'
RSS_DESC = 'Comics and Sketchbook Entries from El Goonish Shive'

ENTRY_TYPE_S = 's'
ENTRY_TYPE_C = 'c'

# Compiled RE
COMIC_COMIC_RE = re.compile(r'^http://www.egscomics.com/\?date=\d{4}-\d{2}-\d{2}#comic$')
SKETCHBOOK_COMIC_RE = re.compile(r'^http://www.egscomics.com/sketchbook/\?date=\d{4}-\d{2}-\d{2}#comic$')

class EGS_Feed(Feed):
    '''
    Defines the class that will support the EGS Feeds. This involves
    fetching both the regular and sketchbook feeds, combining them,
    parsing out the comic image and associated author comments, and
    recombining them into a single RSS feed.
    
    '''
    
    def __init__(self):
        '''
        A simple init. This passes predefined module level constants
        to the parent constructor.
        
        '''
        
        super(EGS_Feed,self).__init__(FEED_NAME, 
                                      FEED_LABEL, 
                                      FEED_DESC, 
                                      FEED_PRIORITY)
    
    def fetch(self):
        '''
        Does the work of fetching the RSS feeds and parsing them. Any new entries
        are found, and the associated comic pages are scraped for comic images
        and author comments. Entries already parsed are retrieved from the database,
        where they are stored for easy access.
        
        '''

        # Let's fetch both the comic and sketchbook feeds and parse them.
        comic_soup = BeautifulSoup(urllib.urlopen(SOURCE_URL_COMIC).read())
        sketchbook_soup = BeautifulSoup(urllib.urlopen(SOURCE_URL_SKETCHBOOK).read())
        
        # Let's loop through the main comic and extract the comics and commentary.
        rss_feed_items = []
        comic_items = comic_soup.find_all('item')
        sketchbook_items = sketchbook_soup.find_all('item')
        
        for source, item in [(ENTRY_TYPE_C,x) for x in comic_items] + [(ENTRY_TYPE_S,x) for x in sketchbook_items]:
            if (source==ENTRY_TYPE_C and not COMIC_COMIC_RE.match(item.link.text.strip())) or (source==ENTRY_TYPE_S and not SKETCHBOOK_COMIC_RE.match(item.link.text.strip())):
                # If it doesn't match this RE, then the entry is not a comic and I will
                # just reproduce it verbatim.
                rss_feed_items.append(PyRSS2Gen.RSSItem(title = item.title.text.strip(),
                                                        link = item.link.text.strip(),
                                                        description = '<b>This entry was not processed. It is shown as-is.</b><br />' + item.description.text.strip(),
                                                        guid = item.guid.text.strip(),
                                                        pubDate = item.pubdate.text.strip()))
            else:
                # In this case, this appears to be a comic, so 
                # we will process it. First, see if we have already
                # processed this entry.
                try:
                    db_entry = EGS_Item.objects.filter(comic_url=item.link.text.strip()).get()
                    image_url = db_entry.image_url
                    commentary_html = db_entry.commentary_html
                except EGS_Item.DoesNotExist:
                    # We haven't previously processed this comic, so let's fetch the full page, parse
                    # out the image URL and commentary, and add it to our database.
                    page_soup = BeautifulSoup(urllib.urlopen(item.link.text.strip()).read())
                    image_url = page_soup.find('div', class_='comic2').contents[0].attrs[u'src'].strip()
                    if not SOURCE_DOMAIN in image_url:
                        t = SOURCE_DOMAIN
                        if source == ENTRY_TYPE_S:
                            t += '/sketchbook'
                        if image_url[0] != '/':
                            t += '/'
                        image_url = t + image_url                    
                    commentary_html = page_soup.find('table', class_='comments')
                    commentary_html.attrs[u'align'] = 'left'
                    for a in commentary_html.find_all('a'):
                        if not re.match(r'^(http(s)?://)?[a-z0-9-]+\.[a-z0-9-\.]+/', a.attrs[u'href']):
                            href = a.attrs[u'href']
                            t = SOURCE_DOMAIN
                            if href[0] != '/':
                                t += '/'
                            href = t + href
                            a.attrs[u'href'] = href
                    commentary_html = unicode(commentary_html)
                    
                    c = EGS_Item(comic_url=item.link.text.strip(),image_url=image_url,commentary_html=commentary_html)
                    c.save()
                    
                # Now we know the image URL, so build our RSS Item.
                rss_feed_items.append(PyRSS2Gen.RSSItem(title = 'El Goonish Shive' + ( ' (Sketchbook)' if source=='sketchbook' else '') + ' - ' + item.title.text.strip(),
                                                        link = item.link.text.strip(),
                                                        description = '<img src="{0}" /><br />{1}'.format(image_url, commentary_html.encode('ascii','ignore')),
                                                        guid = item.guid.text.strip(),
                                                        pubDate = item.pubdate.text.strip()))    
        
        # Construct the final rss feed object and return the text version.
        rss_feed = PyRSS2Gen.RSS2(title = RSS_TITLE,
                                  link = reverse('rss.views.feed', kwargs={'feed_name': FEED_NAME}),
                                  description = RSS_DESC,
                                  lastBuildDate = datetime.datetime.now(),
                                  items = reversed(sorted(rss_feed_items, key=lambda x: datetime.datetime.strptime(x.pubDate[:-4], '%a, %d %b %Y %H:%M:%S').isoformat()))
                                  )
        
        return rss_feed.to_xml()

# Create the feed object that will be used at the package lavel.
feed = EGS_Feed()