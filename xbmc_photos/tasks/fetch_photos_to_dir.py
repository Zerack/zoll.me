'''
James D. Zoll

3/22/2013

Purpose: A script that, when run, will hit xbmc_photos/zip and fetch the file,
         extracting the resulting archive and the pictures to a destination folder,
         completly emptying the folder before doing so.

License: This is a public work.

'''

# System Imports
from urllib import urlopen
from zipfile import ZipFile
import StringIO
import glob
import os

SOURCE_URL = 'http://96.248.69.34/xbmc_photos/zip/'
DESTINATION_DIR = 'C:/Users/Jim/Desktop/XBMC Slideshow Images'

def fetch_photos_to_dir():
    for i in glob.glob(os.path.join(DESTINATION_DIR, '*')):
        os.remove(i)
    
    buffer = StringIO.StringIO()
    buffer.write(urlopen(SOURCE_URL).read())
    photos_zip = ZipFile(buffer,mode='r')    
    photos_zip.extractall(DESTINATION_DIR)

if __name__ == '__main__':
    fetch_photos_to_dir()