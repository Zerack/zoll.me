'''
James D. Zoll

4/15/2013

Purpose: Defines models for the Leap Day application.

License: This is a public work.

'''

from django.db import models


# Note that this is pretty heavily denormalized for better query performance.
# Updates are done by a timed job, and can afford to be slow.
class Good(models.Model):
    numeric_key = models.IntegerField()
    key = models.CharField(max_length=100)
    level = models.IntegerField(null=True)
    display_name = models.CharField(max_length=100)    
    multiplier = models.FloatField(null=True)
    base_value = models.IntegerField(null=True)
    num_ingredients = models.IntegerField(null=True)
    description = models.CharField(max_length=1000)
    shopkeeper = models.CharField(max_length=100,null=True)
    occupation = models.CharField(max_length=1000,null=True)
    ingredient_0 = models.CharField(max_length=100,null=True)
    ingredient_1 = models.CharField(max_length=100,null=True)
    ingredient_2 = models.CharField(max_length=100,null=True)
    ingredient_3 = models.CharField(max_length=100,null=True)
    ingredient_4 = models.CharField(max_length=100,null=True)