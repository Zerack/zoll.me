'''
James D. Zoll

1/2/2013

Purpose: Defines the required views for the My Year In Temperatures scarf application.

License: This is a public work.

'''

# System Imports
from datetime import datetime
import random
from colorsys import hsv_to_rgb
import itertools

# Library Imports
from django.shortcuts import render_to_response
from django.template import RequestContext

# Local Imports
from models import City
from util import rgb_to_hex, darken_hex, parse_scarf_config, get_color_index, get_text_color_class
from scarf.util import ScarfConfigError
from constants import *

def index(request, city=None, year=None, temperature_config=None):
    '''
    Renders the index page of the scarf application, which is the page that allows you to 
    define a city, year, and temperature / color ranges. This page can take parameters, in which case
    it will pre-select options, or it can take no parameters, in which case all of the defaults
    will be used.
    
    Keyword Arguments:
    city -> String. Name of a city. Can contain alphanumeric as well as ()., and <space>. Default None.
    year -> String. Must match '^\d{4}$'. Default None.
    temperature_config -> String. An alternating, '/' delimited list of colors and temperatures. See
                          scarf.util.parse_scarf_config for more information. Default None.
    
    '''

    # Define the object that we will pass to the templating engine. The contents of this will change depending on specifics
    # of the request parameters and such.
    template_dict = {}
    
    # We always need the list of cities and years for populating selects..
    template_dict['cities'] = map(lambda x: x.city, sorted(City.objects.all(), key=lambda x: x.city))
    template_dict['years'] = range(DATA_START_YEAR, datetime.now().year + 1)[::-1]
    
    # The template also always needs this information. Minimum and maximum number of colors, the factor to darken hex
    # by (for the JS clientside darken function), the two classes for white and black text (for dynamic class switching
    # in the client), the max and min valid temperature, and the golden ratio conjugate (for JS client-side random color
    # generation).
    template_dict['min_colors'] = MIN_COLORS
    template_dict['max_colors'] = MAX_COLORS
    template_dict['darken_factor'] = COLOR_DARKEN_FACTOR
    template_dict['text_color_class_white'] = TCC_WHITE
    template_dict['text_color_class_black'] = TCC_BLACK
    template_dict['max_temperature'] = MAX_TEMPERATURE
    template_dict['min_temperature'] = MIN_TEMPERATURE
    template_dict['golden_ratio_conjugate'] = GOLDEN_RATIO_CONJUGATE
        
    # Now, check for the presence of a city or year parameter in the request. If they do not exist, we will dummy 
    # them in as the first entry in the cities list and the first entry in the year list. We do this prior to parsing
    # since these values are required.
    if city == '' or city is None:
        city = template_dict['cities'][0]
    if year is None:
        year = template_dict['years'][0]
    
    template_dict['city_selected'] = city    
    try:
        year = int(year)
    except ValueError:
        year = template_dict['years'][0] 
    template_dict['year_selected'] = year
    
    # Now we will attempt to parse the passed parameters (with our bit of city / year magic included). If the parse succeeds,
    # we can use the data we found. If it doesn't, we have to fake the colors and temperatures.
    try:
        city, year, colors, labels, temperatures = parse_scarf_config(city, year, temperature_config)
        
    except ScarfConfigError:
        # If we caught an error, the problem has to be in the temperature_config variable, because
        # we forced city and year to be valid values prior to calling the parse_scarf_config routine.
        # Therefore, we will now generate fake colors and temperatures to initially populate everything.
        if temperature_config is not None:
            template_dict['message'] = ('warning', 'Hey!', 'Something wasn\'t quite right with your request, and we weren\'t able to load your color or temperature selections. Please try again.')
        
        colors = []
        labels = []
        h = random.random()
        for _ in itertools.repeat(None, DEFAULT_NUM_COLORS):            
            h += GOLDEN_RATIO_CONJUGATE
            h %= 1
            new_color = hsv_to_rgb(h, HSV_S, HSV_V)
            colors.append(rgb_to_hex(map(lambda x: int(x * 255), new_color)))
            labels.append(None)
        
        temperatures = map(lambda x: DEFAULT_COLDEST_TEMP + x* DEFAULT_COLOR_INTERVAL, range(0, DEFAULT_NUM_COLORS - 1))

    # At this point, the color and temperature variables contain either the data from the request, or
    # demonstration data that we have mocked up. Populate the darkened colors and the position list,
    # and then render the template.
    colors_dark = [darken_hex(color, COLOR_DARKEN_FACTOR) for color in colors]
    text_color_classes = [get_text_color_class(color) for color in colors]
    temperature_positions = [(100.0 / len(colors)) * x for x in range(1, len(temperatures) + 1)]
    template_dict['colors'] = zip(colors, colors_dark, labels, text_color_classes)
    template_dict['temps'] = zip(temperatures, temperature_positions)
    template_dict['color_length'] = 100.0 / len(colors)
    
    # Put it all together and render the template.
    return render_to_response(TEMPLATE_INDEX,
                              template_dict,
                              context_instance = RequestContext(request))

def results(request, city=None, year=None, temperature_config=None):
    '''
    Given valid city, year, colors, and temperatures, this will render
    the resulting scarf. the city or year is a valid value but not in the database,
    we show a no data found error. If any parameters are honestly invalid, we 
    pop up a big red box.
    
    Keyword Arguments:
    city -> String. Name of a city. Can contain alphanumeric as well as ()., and <space>. Required.
    year -> String. Must match '^\d{4}$'. Required.
    temperature_config -> String. An alternating, '/' delimited list of colors and temperatures. See
                          scarf.util.parse_scarf_config for more information. Required.
    
    '''
    
    # Define our template object, for convenience.
    template_dict = {}
    
    try:
        # First, we will parse_input, which fails if something isn't correct.
        city, year, colors, labels, temperatures = parse_scarf_config(city, year, temperature_config)
        
        # Since the parse passed, we will set some required information for the template.
        template_dict['valid'] = True
        template_dict['param_city'] = city
        template_dict['param_year'] = year
        template_dict['param_temperature_config'] = temperature_config
        
        # Colors are processed into a tuple with four data points. (hex_color, hex_color_darkened, label, text_color_class)
        darkened_colors = [darken_hex(color, COLOR_DARKEN_FACTOR) for color in colors]
        text_color_classes = [get_text_color_class(color) for color in colors]
        template_dict['colors'] = zip(colors, darkened_colors, labels, text_color_classes)
        template_dict['color_length'] = 100.0 / len(colors)
        
        # Note for the template if we've defined all of the color labels.
        template_dict['missing_labels'] = True if len(filter(lambda x: x == '', labels)) > 0 else False
        
        # Determine the layout for the temperature indicators in the progress bar area.
        temperature_positions = [(100.0 / len(colors)) * x for x in range(1, len(temperatures) + 1)]
        template_dict['temperatures'] = zip(temperatures, temperature_positions)
        
        # Now it's time to pull data for the given city and year. If we have data, we will display it. If no data could be found (either missing data, or weird entry),
        # we show a warning message to the user.
        temperature_data = City.objects.filter(city=city)[0].temperatures_set.all().filter(date__gt=datetime(int(year)-1, 12, 31)).filter(date__lt=datetime(int(year)+1,1,1)).order_by('-date')
        template_dict['no_data'] = len(temperature_data) == 0
        if len(temperature_data) != 0:
            template_dict['data_end'] = temperature_data[0].date
            template_dict['data_start'] = temperature_data[len(temperature_data) - 1].date
            
            # Finally, we will format the temperature data for passing to the template.
            scarf_data = []
            for data_idx, data_point in enumerate(temperature_data):
                month_string = data_point.date.strftime('%B')
                if month_string not in map(lambda x: x[0], scarf_data):
                    scarf_data.append((month_string,[]))
                # Each scarf data point takes the following format:
                # (date, temp, color, label, text_color_class, index)
                #
                # NB: When we fetch from the previously populated template_dict['colors'], we dummy out the darkened
                # color result, since this is used to generate style elements. Since we are going to assign colors
                # by CSS class like .bar-000000, we don't actually need to know the darkened color value here.
                color_index = get_color_index(data_point.average_temp, temperatures)
                cur_color, dummy_darkened_color, cur_label, cur_text_color_class = template_dict['colors'][color_index]
                scarf_data[-1][1].append((data_point.date, data_point.average_temp, cur_color, cur_label, cur_text_color_class, data_idx))
            template_dict['scarf_data'] = scarf_data
        
        # The last step is to check for and utilize the cookie that counts the number of checked rows.
        template_dict['checked_row_count_cookie'] = CHECKED_ROW_COUNT_COOKIE
        if CHECKED_ROW_COUNT_COOKIE in request.COOKIES:
            try:
                template_dict['checked_row_index'] = len(temperature_data) - int(request.COOKIES[CHECKED_ROW_COUNT_COOKIE])
            except:
                template_dict['checked_row_index'] = len(temperature_data)
        else:
            template_dict['checked_row_index'] = len(temperature_data)
            
        
    except ScarfConfigError:
        # ScarfConfigError is thrown when the passed city, year, and temperature_config are malformed in some way.
        # This will display a minimal error page to the user with a link to start over.
        template_dict['valid'] = False
        template_dict['message'] = ('error','Don\'t Blame Me.','One or more of the parameters for your scarf was corrupt, missing, or invalid, and your scarf could not be created. Sorry!')
    
    return render_to_response(TEMPLATE_RESULTS,
                              template_dict,
                              context_instance = RequestContext(request))

