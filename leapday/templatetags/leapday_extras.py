'''
Created on Mar 29, 2013

@author: Jim
'''

from django import template
register = template.Library()

@register.filter()
def good_css_name(value):
    return value.display_name.lower().replace(' ','-')

@register.filter()
def base_goods_ordered_set(value):
    ret = sorted(value.base_ingredients.all(), key=lambda x: x.ingredient.value)
    ret = ret[1:] + [ret[0]]
    return ret

@register.filter()
def unique_products(value):
    return sorted(filter(lambda x: x.num_ingredients <= 5, list(set([x.product for x in value.recipes.all()]))), key=lambda x: x.value)