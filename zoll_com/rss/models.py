'''
James D. Zoll

4/2/2013

Purpose: Defines models for the RSS application.

License: This is a public work.

'''

# Library Imports
from django.db import models

class CH_Item(models.Model):
    # Defines information needed to cache entries for the CH feed.
    comic_url = models.CharField(max_length=200,unique=True)
    image_url = models.CharField(max_length=200)
    
class EGS_Item(models.Model):
    comic_url = models.CharField(max_length=200,unique=True)
    image_url = models.CharField(max_length=200)
    commentary_html = models.CharField(max_length=5000)
    
class Scarf_Item(models.Model):
    pub_date = models.DateTimeField()
    max_data_date = models.DateField()