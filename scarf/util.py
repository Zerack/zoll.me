'''
James D. Zoll

1/2/2013

Purpose: This utility module holds several color helper functions as well as the required logic to parse
         the scarf URL temperature_config parameter.

License: This is a public work.

'''

# System Imports
import re
from colorsys import rgb_to_hls

# Local Imports
from constants import TCC_WHITE, TCC_BLACK, MIN_COLORS, MAX_COLORS, MIN_TEMPERATURE, MAX_TEMPERATURE

# Constant Definitions for color space conversion.
HEX = '0123456789abcdef'
HEX2 = dict((a+b, HEX.index(a)*16 + HEX.index(b)) for a in HEX for b in HEX)

def hex_to_rgb(hexadecimal):
    '''
    Converts a hexadecimal color value to a tuple of (r,g,b).
    
    Keyword Arguments:
    hex -> String. The hexadecimal input in '000000' format. Required.
    
    '''
    
    hexadecimal = hexadecimal.lower()
    return (HEX2[hexadecimal[0:2]], HEX2[hexadecimal[2:4]], HEX2[hexadecimal[4:6]])

def rgb_to_hex(rgb):
    '''
    Converts a tuple of (r,g,b) to its hexadecimal notation in the form '000000'
    
    Keyword Arguments:
    rgb -> Tuple of (r,g,b). The color to convert to hexadecimal. Required.
    
    '''
    
    return format((rgb[0]<<16)|(rgb[1]<<8)|rgb[2], '06x')

def darken_hex(value, arg):
    ''' 
    Darkens a hexadecimal string in the format '000000' by a factor of <arg>, where arg is the percent to move towards black.
    
    Keyword Arguments:
    value -> String. The hexadecimal color to start with in the format '000000'. Required.
    arg -> Float. Value in the range [0, 1.0] representing how far towards black to go. Required.
    
    '''
    
    try: 
        arg = float(arg)
        rgb = hex_to_rgb(value)
    except:
        return value
    
    rgb = map(lambda x: int(x * (1.0 - arg)), rgb)    
    return rgb_to_hex(rgb)

class ScarfConfigError(Exception):
    '''
    Generic class for exceptions when parsing the city, year, and
    temperature_config variables of a scarf URL
    
    '''
    
    pass

def parse_scarf_config(city, year, temperature_config):
    '''
    Validates the passed city, year, and temperature_config and
    processess temperature_config to split it into lists of colors,
    labels, and temperatures. Raises ScarfConfigError if parsing 
    cannot be completed.
    
    Keyword Arguments:
    city -> String. The city. Can include (),.<space>. Required.
    year -> String/Integer. Must be an integer. Required.
    temperature_config -> String. This is a forward-slash delimited list
                          of alternating color/label pairs and temperatures.
                          
                          For example: pair/temp/pair/temp/pair
                          
                          The list must start and end with a pair. Pairs are defined
                          as 6 hexadecimal digits followed by a "-", and then a-zA-Z0-9
                          defining the color label, so for example "000000-White".
                          
                          Temperatures are defined as floating point numbers, so just
                          something like "-10.4" is fine.
                          
                          That all said, a final (short) temperature_config might look like:
                          "000000-White/30.0/00FF00-Maybe Blue/45.0/FF0000-Getting Hotter"
                          
                          See scarf.urls for an explicit regexp definition.
                          
    '''    
    
    if city == '' or city is None:
        raise ScarfConfigError('Invalid city: "{0}". City cannot be empty or None'.format(city))
    
    try:
        year = int(year)
    except:
        raise ScarfConfigError('Invalid year: "{0}". Year must be an integer.'.format(year))
    
    try:
        temperature_config = temperature_config.split('/')
    except:
        raise ScarfConfigError('Invalid colors and temperatures: "{0}". Unable to split string from URL'.format(temperature_config))
    
    colors_labels = temperature_config[0::2]
    temperatures = temperature_config[1::2]
        
    # There must be at least MIN_COLORS colors.
    if len(colors_labels) < MIN_COLORS:
        raise ScarfConfigError('Invalid colors: "{0}". There must be at least {1} color(s).'.format(colors_labels, MIN_COLORS))
    
    # There can be no more than MAX_COLORS colors.
    if len(colors_labels) > MAX_COLORS:
        raise ScarfConfigError('Invalid colors: "{0}". There can be no more than {1} color(s).'.format(colors_labels, MAX_COLORS))
    
    # There must be exactly one more color than temperatures.
    if len(colors_labels) != len(temperatures) + 1:
        raise ScarfConfigError('Invalid colors and temperatures: "{0}", "{1}". Must have one more color and than temperature.'.format(colors_labels, temperatures))
        
    # Now we will will validate that the list of temperatures is good. This requires first converting them all
    # to floating point numbers. 
    try:
        temperatures = [float(t) for t in temperatures]
    except:
        raise ScarfConfigError('Invalid temperatures: "{0}". Unable to convert temperatures to floating point.'.format(temperatures))
    
    # Temperatures must be between MIN_TEMPERATURE and MAX_TEMPERATURE, inclusive.
    if any(map(lambda x: x < MIN_TEMPERATURE or x > MAX_TEMPERATURE, temperatures)):
        raise ScarfConfigError('Invalid temperatures: "{0}". Temperatures must be in the range [{1},{2}]'.format(temperatures, MIN_TEMPERATURE, MAX_TEMPERATURE))
        
    # Temperatures must be sorted in ascending order.
    if sorted(temperatures) != temperatures:
        raise ScarfConfigError('Invalid temperatures: "{0}". Temperatures must be in ascending order.'.format(temperatures))
    
    colors, labels = zip(*map(lambda x: x.split('-'), colors_labels))
    colors = map(lambda x: x.lower(), colors)
    
    # Colors and labels must be valid formats.
    if any(map(lambda x: not re.match(r'^[0-9a-f]{6}$', x, re.IGNORECASE), colors)):
        raise ScarfConfigError('Invalid colors: "{0}". Invalid hexadecimal notation.'.format(colors))
    
    if any(map(lambda x: not re.match(r'^[a-zA-Z0-9 ]*$', x, re.IGNORECASE), labels)):
        raise ScarfConfigError('Invalid labels: "{0}". Invalid characters in label.'.format(labels))
    
    # Everything appears valid, so lets return.
    return (city, year, colors, labels, temperatures)
   

def get_color_index(t, t_list):
    '''
    Returns the correct color bucket index for temperature t, given that
    the temperature splits on the current scarf are at t_list.
    
    Keyword Arguments:
    t -> Float. The temperature to test. Required.
    t_list -> List of Floats. The ascending-ordered list of temperature divisions. Required.
    
    '''
    
    color_index = 0
    while color_index < len(t_list) and t >= t_list[color_index]:
        color_index += 1
    return color_index

def get_text_color_class(color):
    '''
    Quick and dirty color conversion to determine if a bar color should
    display with white or black text overlaid.
    
    Keyword Arguments:
    color -> String. Hexadecimal color in '000000' format. Required.
    
    '''
    rgb_color = hex_to_rgb(color)
    hls_color = rgb_to_hls(*rgb_color)
    if hls_color[1] > 256 / 2:
        return TCC_BLACK
    else:
        return TCC_WHITE