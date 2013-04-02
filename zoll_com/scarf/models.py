'''
James D. Zoll

1/20/2013

Purpose: Defines database models for the scarf tracker.

License: This is a public work.

'''

# Library Imports
from django.db import models

class City(models.Model):
    '''
    Class to hold cities for which we have temperature information.
    
    '''
    
    city = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.city
    
class Temperatures(models.Model):
    '''
    Stores the temperature data (date and average temperature) for cities.
    
    '''
    
    city = models.ForeignKey(City)
    date = models.DateField()
    average_temp = models.DecimalField(max_digits=4, decimal_places=1)

    def __unicode__(self):
        return ','.join(self.city, self.date, self.average_temp)

