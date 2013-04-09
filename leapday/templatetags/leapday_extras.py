'''
Created on Mar 29, 2013

@author: Jim
'''

from django import template
register = template.Library()

from leapday.models import Good

base_goods = list(Good.objects.filter(good_type='goodtype_basic').all())
base_goods.append(Good.objects.filter(key='goodtype_crystal').get())
base_goods.sort(key=lambda x: x.value)

@register.filter()
def good_css_name(value):
    return value.display_name.lower().replace(' ','-')

@register.filter()
def base_goods_ordered_set(value):
    ret = sorted(value.base_ingredients.all(), key=lambda x: x.ingredient.value)
    ret = ret[1:] + [ret[0]]
    return ret