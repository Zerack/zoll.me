'''
James D. Zoll

4/15/2013

Purpose: Defines models for the Leap Day application.

License: This is a public work.

'''

from django.db import models

class Good(models.Model):
    key = models.CharField(max_length=100)
    good_type = models.CharField(max_length=20,choices=[(x, x) for x in ['goodtype_basic','goodtype_crafted','goodtype_crystal']])
    display_name = models.CharField(max_length=100)
    tier = models.IntegerField()
    base_multiplier = models.FloatField()
    base_value = models.IntegerField()
    num_ingredients = models.IntegerField()
    recipe_value_multiplier = models.FloatField()
    total_value_multiplier = models.FloatField()
    value = models.IntegerField()
    description = models.CharField(max_length=1000)
    
    def __unicode__(self):
        return '{0}'.format(self.key)
    
class Recipe_Item(models.Model):
    product = models.ForeignKey(Good, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Good, related_name='recipes')
    display_order = models.IntegerField()
    
    class Meta:
        ordering = ['display_order']
    
class Base_Material(models.Model):
    product = models.ForeignKey(Good, related_name='base_ingredients')
    ingredient = models.ForeignKey(Good, related_name='bases')
    quantity = models.IntegerField()

class Production_Plan(models.Model):
    water = models.IntegerField()
    food = models.IntegerField()
    wood = models.IntegerField()
    stone = models.IntegerField()
    crystal = models.IntegerField()
    
class Production_Plan_Entry(models.Model):
    production_plan = models.ForeignKey(Production_Plan, related_name='entries')
    value = models.IntegerField()
    num_items = models.IntegerField()
    
class Production_Plan_Entry_Goods(models.Model):
    production_plan_entry = models.ForeignKey(Production_Plan_Entry, related_name='goods')
    good = models.ForeignKey(Good)
    quantity = models.IntegerField()