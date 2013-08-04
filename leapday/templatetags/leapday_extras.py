'''
James D. Zoll

4/15/2013

Purpose: Defines template tags for the Leapday Recipedia application.

License: This is a public work.
'''

from django import template
register = template.Library()

@register.filter()
def css_name(value):
    ''' 
    Returns the lower-case hyphen-replaced display name,
    which used as the css class for the good.
    
    Keyword Arguments:
    value -> Good. The good to get the css class for.
    
    '''
    
    return value.lower().replace(' ','-')

@register.filter()
def desc_value_sort(value):
    '''
    Designed to sort the results of .iteritems() on a dict of goods
    for the index.
    
    value -> List of tuples.
    '''
    
    return sorted(value, key=lambda x: x[1]['active']['value'], reverse=True)

@register.filter()
def base_good_display_name(value):
    BASE_GOODS = {'good_water': 'Water',
                  'good_food': 'Food',
                  'good_wood': 'Wood',
                  'good_stone': 'Stone',
                  'goodtype_crystal': 'Crystal'}
    return BASE_GOODS[value]