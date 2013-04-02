'''
Created on Mar 29, 2013

@author: Jim
'''

from django import template
register = template.Library()

import os.path

@register.filter()
def basename(value):
    try:
        return os.path.basename(value)
    except:
        return value