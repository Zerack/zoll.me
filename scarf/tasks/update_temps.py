'''
James D. Zoll
1/21/2013

Purpose: Defines a python method that will fetch temperature data and update the database.

License: This is a commercial work.

'''

# System Imports
from urllib import urlopen
from datetime import date
import re
from zipfile import ZipFile
import StringIO
import datetime
from sys import stdout

# Library Imports
from bs4 import BeautifulSoup
from django.db.models import Max

# Local Imports
from scarf.models import City, Temperatures
from rss.models import Scarf_Item

# Constants
URL_BASE = 'http://academic.udayton.edu/kissock/http/Weather/'
URL_CITYLIST_US = URL_BASE + 'citylistUS.htm'
URL_ARCHIVE = URL_BASE + 'gsod95-current/allsites.zip'

def update_temps(out = None):
    
    # Get standard out.
    if out is None:
        out = stdout
    
    out.write('Storing current maximum date for RSS generation')
    old_max_date = Temperatures.objects.all().aggregate(Max('date'))['date__max']
    
    out.write('Cleaning existing tables')
    # Clean the existing data.
    #Temperatures.objects.all().delete()
    City.objects.all().delete()
    
    # Fetch the new list of cities
    out.write('Fetching US City List from "{0}"'.format(URL_CITYLIST_US))    
    soup = BeautifulSoup(urlopen(URL_CITYLIST_US).read())
    out.write('Parsing US City List')
    
    # Parse out the city entries
    cities = []
    for link in soup.find_all('a'):
        if re.match(r'^[A-Z]{3,8}.txt$', link.text.strip(), re.IGNORECASE):
            # This is a valid link. We want the accompanying city / state name, which due to
            # sillyness with how this page is built, means we go up until we are a LI, and then find the first
            # 'B' tag, and strip and whitespace and trailing (
            city_code = link['href'].split('/')[-1].rstrip('.txt')
            node = link
            while node.name != 'li':
                node = node.parent
                
            city_name = node.find_all('b')[0].text.strip().strip('(').strip()
            out.write( 'Found ID: {0}, City: {1}'.format(city_code.rjust(8), city_name))
            cities.append((city_name, city_code))    
    out.write('Found {0} Cities'.format(len(cities)))

    # Download the temperature data archive
    out.write('Downloading data archive')
    buffer = StringIO.StringIO()
    buffer.write(urlopen(URL_ARCHIVE).read())
    archive = ZipFile(buffer,mode='r')
    #archive = ZipFile('allsites.zip','r')
    
    # Parse out the desired data from the archive and insert it.
    out.write('Parsing data archive')
    for idx, city in enumerate(cities):
        out.write('Inserting {0} of {1}: {2}'.format(str(idx+1).rjust(len(str(len(cities))),'0'), len(cities), city[0]))
        
        c = City(city=city[0])
        c.save()
        bulk_data = []
                
        for line in archive.open('{0}.txt'.format(city[1])).read().split('\r\n'):
            if line == '':
                continue
            month = int(line[1:3])
            day = int(line[15:17])
            year = int(line[29:33])
            temp = float(line[42:47].strip())
        
            bulk_data.append((c, date(year, month, day), temp))
            
        Temperatures.objects.bulk_create([Temperatures(city=x[0], date=x[1], average_temp=x[2]) for x in bulk_data])    
    buffer.close()
    
    # Now we might have to make a new RSS entry.
    new_max_date = Temperatures.objects.all().aggregate(Max('date'))['date__max'] 
    if new_max_date > old_max_date:
        out.write('Data has updated. Adding RSS feed entry.')
        s = Scarf_Item(pub_date = datetime.datetime.now(), max_data_date = new_max_date)
        s.save()
    else:
        out.write('Data has not updated. No RSS feed entry required.')
    
    # All done.
    out.write('Processing complete!')            
    
if __name__ == '__main__':
    update_temps()