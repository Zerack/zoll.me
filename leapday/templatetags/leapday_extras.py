'''
James D. Zoll

4/15/2013

Purpose: Defines template tags for the Leapday Recipedia application.

License: This is a public work.
'''

from django import template
register = template.Library()

@register.filter()
def good_css_name(value):
    ''' 
    Returns the lower-case hyphen-replaced display name,
    which used as the css class for the good.
    
    Keyword Arguments:
    value -> Good. The good to get the css class for.
    
    '''
    
    return value.display_name.lower().replace(' ','-')

@register.filter()
def base_goods_ordered_set(value):
    '''
    Returns a set of the base goods required for an object's creation,
    ordered by the desired order. In this case, that order is value low 
    to high, with the "Other" good on the end instead of the front.
    
    Additionally, this attempts first to load goods from the
    shim_base_ingredients attribute, which is present in some situations
    where the attribute has been preloaded to prevent excessive DB IO.
    
    Keyword Arguments:
    value -> Good. The good for which to return the list of ingredients.
    
    '''
    
    try:
        base_goods = value.shim_base_ingredients
    except:
        base_goods = value.base_ingredients.all()
    ret = sorted(base_goods, key=lambda x: x.ingredient.value)
    ret = ret[1:] + [ret[0]]
    return ret
