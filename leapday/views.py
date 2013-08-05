'''
James D. Zoll
4/5/2013

Purpose: Defines application views for the Leap Day recipedia application.

License: This is a public work.

'''
# System Imports
import json
import pprint
from math import ceil
from collections import OrderedDict

# Library Imports
from django.shortcuts import render_to_response, get_object_or_404, HttpResponse
from django.template import RequestContext

# Local Imports
from leapday.models import Good

# Constants for the Goods page. Mostly for tree generation.
ICON_WIDTH = 47
ICON_HEIGHT = 58
ROW_BUFFER = 20
BOTTOM_ATTACH_YBUFFER = 3
TOP_ATTACH_YBUFFER = -10
SIDE_ATTACH_XBUFFER = ICON_WIDTH * 0.2

def index(request, hash):    
    '''
    Returns the index page of the application, which shows the interactive
    list of recipes.
    
    '''
    
    # Parse out the hash, determining the numeric keys and 
    # levels to activate. Anything not present is assumed level 0.
    # Levels passed for harvestable goods are just ignored silently.
    i = 0
    recipe_levels = {}
    while i < len(hash):
        nk = int(hash[i:i+2], 36)
        l = int(hash[i+2], 36) # This only goes up to 30 (u), but we can use the builtin base 36 conversion.
        
        # Add to our dict of non-zero recipes.
        recipe_levels[nk] = l
                
        i += 3        
    
    # Grab the goods list and construct our object, being sure to
    # activate the appropriate level for each good.
    goods_db = Good.objects.order_by('key','level').all()
    goods_all = {}
    for good in goods_db:
        if good.key == 'good_junk':
            continue
        # Add the good record to the goods_all hash if it doesn't yet exist.
        if good.key not in goods_all:
            goods_all[good.key] = {'display_name': good.display_name,
                                   'description': good.description,
                                   'numeric_key': good.numeric_key,
                                   'active': {'level': good.level if good.numeric_key not in recipe_levels else recipe_levels[good.numeric_key],
                                              'references': {}},
                                   'levels': {}}
        # If this is a base ingredient, clean up after ourselves a bit. We go
        # ahead and populate the basic information for these here.
        if good.base_value is not None:
            goods_all[good.key]['active']['value'] = good.base_value
            goods_all[good.key]['active']['total_multiplier'] = 1
            goods_all[good.key]['active']['materials'] = OrderedDict([('good_water', 0),
                                                                      ('good_food', 0),
                                                                      ('good_wood', 0),
                                                                      ('good_stone', 0),
                                                                      ('goodtype_crystal', 0)])
            if good.key in ['good_water','good_food','good_wood','good_stone','good_crystal']:
                material_key = good.key
            else:
                material_key = 'goodtype_crystal'
            goods_all[good.key]['active']['materials'][material_key] += 1
            del goods_all[good.key]['levels']
            del goods_all[good.key]['active']['level']
        else:        
            # Now add the current level information, since this is not a base
            goods_all[good.key]['levels'][good.level] = {'multiplier': good.multiplier,
                                                         'ingredients': filter(lambda x: x is not None, [good.ingredient_0,
                                                                                                         good.ingredient_1,
                                                                                                         good.ingredient_2,
                                                                                                         good.ingredient_3,
                                                                                                         good.ingredient_4]),
                                                         }
    
    # We have to iterate through our goods list and update all of the ingredients lists, as
    # well as populating the active ingredients item. We will add the display name properties
    # to them, since these are needed for tooltips.
    for key, good in goods_all.iteritems():
        if 'levels' in good:
            for level in good['levels'].iterkeys():
                good['levels'][level]['ingredients'] = map(lambda x: {'key': x, 'display_name': goods_all[x]['display_name']}, good['levels'][level]['ingredients'])
            good['active']['ingredients'] = good['levels'][good['active']['level']]['ingredients']
                
        
    # Now we will add to our goods_all a hash for each item containing keys
    # for all of the other active items that reference it. This can be updated
    # on the fly on the web side of things
    for key, good in goods_all.iteritems():
        if 'levels' in good:        
            for i in good['levels'][good['active']['level']]['ingredients']:
                goods_all[i['key']]['active']['references'][key] = True
            
    # Now we loop through all the goods and calculate the VALUE, TOTAL MULT,
    # and BASE MATERIALS information. Value and base materials are calculated
    # recursively, while total mult is just a function of these two.
    #
    # NB: Value appears to be ceilinged to the next integer PER ITEM.
    #     This needs to be confirmed, though.
    def calc_good(g):
        value = 0
        materials = OrderedDict([('good_water', 0),
                                 ('good_food', 0),
                                 ('good_wood', 0),
                                 ('good_stone', 0),
                                 ('goodtype_crystal', 0)])
        materials_value = 0
        for i in g['levels'][g['active']['level']]['ingredients']:
            if 'value' not in goods_all[i['key']]['active']:
                calc_good(goods_all[i['key']])
            value += goods_all[i['key']]['active']['value']
            materials_value += float(goods_all[i['key']]['active']['value']) / float(goods_all[i['key']]['active']['total_multiplier'])
            for k in materials.iterkeys():
                materials[k] += goods_all[i['key']]['active']['materials'][k]
        value = int(ceil(value * g['levels'][g['active']['level']]['multiplier']))
        g['active']['value'] = value
        g['active']['total_multiplier'] = float(value) / float(materials_value)
        g['active']['materials'] = materials
    
    for good in goods_all.itervalues():
        if 'value' not in good['active']:
            calc_good(good)
    
    # All done, pass it off to the templating engine.
    return render_to_response('leapday/index.html', {'goods_all': goods_all, 'goods_all_json': json.dumps(goods_all), 'hash': hash, 'recipe_levels_json': json.dumps(recipe_levels)}, context_instance = RequestContext(request))

def good(request, key, hash):
    '''
    Returns a page detailing information about the selected good. This includes
    icon, cost, flavor text, and production information. The majority of code
    in this view is dedicated to setting up the production web, which requires
    placing icons onto a canvas.
    
    Keyword Arguments:
    key -> String. The unique identifier for the good.
    
    '''
    
    # First things first. We need to decode the given hash and make a dictionary of keys and levels.
    i = 0
    recipe_levels = {}
    while i < len(hash):
        nk = int(hash[i:i+2], 36)
        l = int(hash[i+2], 36) # This only goes up to 30 (u), but we can use the builtin base 36 conversion.
        
        # Add to our dict of non-zero recipes.
        recipe_levels[nk] = l
                
        i += 3  
    
    # Next, we need to fetch all of the data. Since we can't determine what we need for the tree view
    # without looking at the data itself, we go ahead and pull everything.
    goods_db = Good.objects.all()
    
    # Now we filter these objects a bit. We keep base goods, goods at level 0 that aren't in
    # our recipe_levels object, and recipes of matching level if they are.
    goods_db_filtered = filter(lambda x: x.level is None or (x.level == 0 and x.numeric_key not in recipe_levels) or (x.numeric_key in recipe_levels and x.level == recipe_levels[x.numeric_key]), goods_db)
    
    # We need to be able to reference things by key, so we'll set that up here with what's left.
    goods = {}
    for cur_good in goods_db_filtered:
        goods[cur_good.key] = cur_good
    
    # Logic to build the simple information on the page. This includes things like icon,
    # flavor text, etc. etc.
    td = {}
    td['display_name'] = goods[key].display_name
    td['description'] = goods[key].description
    td['ingredients'] = map(lambda x: {'key':x, 'display_name': goods[x].display_name},filter(lambda x: x is not None, [goods[key].ingredient_0,
                                                                                                                        goods[key].ingredient_1,
                                                                                                                        goods[key].ingredient_2,
                                                                                                                        goods[key].ingredient_3,
                                                                                                                        goods[key].ingredient_4]))
    td['recipe_multiplier'] = goods[key].multiplier
    
    # Calculating value, total multiplier, and base materials has to be done recursively.
    # We will calculate the value of each of my ingredients (with a cache for duplicates)
    # and then finally arrive at values for me. We don't need to be able to recall this
    # information later, so we won't worry too much about it.
    stats_cache = {}
    def calc_good(g):
        if g.key in stats_cache:
            return 
        
        if g.level is None:
            # This is a base good, so a little special handling.
            stats_cache[g.key] = {'value': g.base_value,
                                  'total_multiplier': 1.0,
                                  'materials': OrderedDict([('good_water', 0),
                                                             ('good_food', 0),
                                                             ('good_wood', 0),
                                                             ('good_stone', 0),
                                                             ('goodtype_crystal', 0)])}
            stats_cache[g.key]['materials'][g.key] += 1
            return
        
        value = 0
        materials = OrderedDict([('good_water', 0),
                                 ('good_food', 0),
                                 ('good_wood', 0),
                                 ('good_stone', 0),
                                 ('goodtype_crystal', 0)])
        materials_value = 0
        for i in filter(lambda x: x is not None, [g.ingredient_0,
                                                  g.ingredient_1,
                                                  g.ingredient_2,
                                                  g.ingredient_3,
                                                  g.ingredient_4]):
            if i not in stats_cache:
                calc_good(goods[i])
            value += stats_cache[i]['value']
            materials_value += float(stats_cache[i]['value']) / float(stats_cache[i]['total_multiplier'])
            for k in materials.iterkeys():
                materials[k] += stats_cache[i]['materials'][k]
        value = int(ceil(value * g.multiplier))
        total_multiplier = float(value) / float(materials_value)
        stats_cache[g.key] = {'value': value,
                              'total_multiplier': total_multiplier,
                              'materials': materials}
                
    calc_good(goods[key])
    
    td['value'] = stats_cache[key]['value']
    td['total_multiplier'] = stats_cache[key]['total_multiplier']
    td['base_materials'] = stats_cache[key]['materials']
    
    # To determine what this item is used to craft, we have to actively check all ingredients lists
    # for all goods in the current set. This is a pain, but there's no way to precalculate this
    # information short of just caching it. We'll end up doing this alphabetically, since
    # that way we don't have to calculate values for all items (which is a pain, and slow)
    td['used_to_craft'] = []
    for cur_good in goods.itervalues():
        if cur_good.key == key:
            continue
        elif len(filter(lambda x: x == key, filter(lambda x: x is not None, [cur_good.ingredient_0,
                                                                             cur_good.ingredient_1,
                                                                             cur_good.ingredient_2,
                                                                             cur_good.ingredient_3,
                                                                             cur_good.ingredient_4]))) > 0:
            td['used_to_craft'].append({'key': cur_good.key, 'display_name': cur_good.display_name})
    td['used_to_craft'].sort(key=lambda x: x['display_name'])
    
    good_tree_cache = {}
    def get_recipe_tree(g, g_depth=0):
        ''' 
        Returns a tree object representing a hierarchical view
        of how a good is created. This necessarily involves a number
        of database queries, but we'll try to minimize this through caching
        subtrees that we have already generated.
        
        Keyword Arguments:
        g -> Good. The good at the top node of the current tree.
        g_depth -> Int. The current depth from the original top node. This
                   is used in build_recipe_list when building the list format 
                   of this tree to determine what row this item should reside on.
        '''
        
        # If we've cached this sub-tree, use it.
        if g.key in good_tree_cache:
            return good_tree_cache[g.key]
        
        # We need to fetch the information, so start with the ingredients. We'll allow
        # the query for 'recipe ingredients' to execute normally without a prefetch, but
        # we'll make sure to prefetch the ingredient information to reduce database hits.
        r = {'good': g}
        r_i = [goods[x] for x in filter(lambda x: x is not None, [g.ingredient_0, 
                                                                  g.ingredient_1, 
                                                                  g.ingredient_2, 
                                                                  g.ingredient_3, 
                                                                  g.ingredient_4])]
        num_children = len(r_i)
        num_unique_children = len(set(r_i))
        
        # Depending on the relationship between the number of children and
        # the number of unique children, we manipulate the 'children', 'leaves',
        # 'depth', and 'children_mult' dictionary attributes. These attributes
        # are all part of the setup for turning this tree structure into a list
        # for display by the templating engine.
        if num_children > 0:
            # Since this good has children, it is not a terminal good.
            if num_children > 1 and num_unique_children == 1:
                # This is a special recipe, requiring only a single type of good,
                # but requiring more than one of it. This will eventually be displayed
                # with a text multiplier in the tree, to conserve visual space.
                r['children'] = [get_recipe_tree(r_i[0], g_depth+1)]
                r['children_mult'] = num_children
                r['leaves'] = r['children'][0]['leaves']
                r['depth'] = 1+ r['children'][0]['depth']
            else:
                # This is a more standard recipe, so we just display the usual attributes.
                r['children'] = [get_recipe_tree(x, g_depth+1) for x in r_i]
                r['leaves'] = sum(map(lambda x: x['leaves'], r['children']))
                r['depth'] = 1+ max(map(lambda x: x['depth'], r['children']))
        else:
            # With no children, this is a terminal good. More specifically, this
            # is a basic good, "Other", or crystal.
            r['leaves'] = 1
            r['depth'] = 0
        
        # Cache the tree result for use if we encounter this item again while tree building.
        good_tree_cache[g.key] = r
        return r
    
    def build_recipe_list(t, level, rl):
        '''
        Recursively converts the recipe tree in t into an ordered
        display list in rl. Note that this operates recursively, but doesn't
        return a value. Instead, it uses the rl object and modifies it at each
        level.
        
        Keyword Arguments:
        t -> Dict. The current head of the tree being processed.
        level -> Int. The "depth" we are at. This is reversed from depth
                 inserted into leaves during tree building, as that
                 value was used to determine the maximum depth.
        rl -> List of Lists. The recipe list object, where will will put all of our output.
        
        '''
        
        # Since we are traversing the tree depth first and left to right, we can
        # always append newly encountered entries to the appropriate index in rl.
        # As long as we know the correct width of the entry (based on the number of terminal
        # nodes underneath it), we can add that in and guarantee correct final positioning.
        rl[level].append({'good': t['good'], 'size': t['leaves'], 'num_bottom_attach_points': 0 if 'children' not in t else len(t['children'])})
        
        # If this is one of those special recipes that requires additional text, add that to the object we just created.
        if 'children_mult' in t:
            rl[level][-1]['mult'] = t['children_mult']
            
        # Now, if the current tree head has children, perform the same set of operations on the children. We
        # don't do any caching here for two reasons.
        #
        # 1) The positions are different, so we need to iteratively add them as required.
        # 2) There shouldn't be any database IO happening here, so we're in pure Python.        
        if 'children' in t:
            for child in t['children']:
                build_recipe_list(child, level + 1, rl)
        else:
            # Since there are no children, we have two cases. First, we're at max depth
            # and can go back up the tree without doing anything. Second, we're at a 
            # terminal leaf, but aren't at max depth. In this case, in order to get spacing
            # correct, we have to fabricate a fake tree head that will cascade to the lowest
            # depth, while adding None goods, which we will later ignore, but are required now
            # for positioning.
            if level < max_depth:
                build_recipe_list({'good': None, 'leaves': t['leaves']}, level + 1, rl)
    
    def find_list_entry(x_pos, depth):
        '''
        This is used to find the "parent" node of an entry
        once it has been converted to a list. It checks the row
        above the current one, and counts from the left until an appropriate
        result is found. This function assumes that recipe_list is defined,
        since it will be (and this function is only used here)
        
        Keyword Arguments:
        x_pos -> Int. The x position (cardinality, not pixels) of the item we 
                 want to find the parent of.
        depth -> Int. The depth (again, index, not pixels) at which
                 we are to look for a parent.
                 
        '''
        
        filled_leaves = 0
        for i in recipe_list[depth]:
            item_start = filled_leaves
            item_end = filled_leaves + i['size']
            if item_start <= x_pos and x_pos < item_end:
                return i
            else:
                filled_leaves += i['size']
    
    def build_bezier(line):
        '''
        Given a 4-tuple of (x1, y1, x2, y2), returns an 8-tuple of 
        (x1, y1, x2, y2, x3, y3, x4, y4), defining the start, stress1, stress2,
        and end of a bezier curve. This is used to draw beziers on the canvas
        to connect items in the production tree.
        
        Keyword Arguments:
        line -> 4-tuple of (x1, y1, x2, y2) defining a line.
        
        '''
        
        if line[0] == line[2]:
            # In the unique case where the line is vertical, we
            # just push in inflection points at 1/3 and 2/3 of line height.
            # This has no effect on the visual presentation of the line.
            x_increment = (line[2] - line[0]) / 3.0
            y_increment = (line[3] - line[1]) / 3.0
        
            line = (line[0],line[1],line[0]+x_increment, line[1] + y_increment, line[0]+ (2*x_increment), line[1]+(2*y_increment),line[2],line[3])
        else:
            # In the case where the line has horizontal run, we put the two inflection points at the y-midpoint, directly
            # above / below each of the two x coordinates. This results in a nice looking bezier.
            line = (line[0], line[1], line[0], (line[3] + line[1]) / 2, line[2], (line[3] + line[1]) / 2, line[2], line[3])            
        return line
    
    # Recipe tree building starts here.
    recipe_tree = get_recipe_tree(goods[key])  
    
    max_depth = recipe_tree['depth']
    leaves = recipe_tree['leaves']
    
    # Make the recipe list.
    recipe_list = [[] for x in range(max_depth + 1)]
    build_recipe_list(recipe_tree, 0, recipe_list)
    
    # Now we'll actually begin building the final presentation
    # logic.    
    tree_width = ICON_WIDTH * leaves
    tree_height = ICON_HEIGHT * (max_depth + 1) + (ROW_BUFFER * max_depth) 
    
    # recipe_beziers stores the beziers that will be written to a javascript array
    # and drawn on the canvas.
    recipe_beziers = []
    
    # recipe_mults stores the multiple good indicators (x3, x5) that will be drawn
    # on recipes that require it.
    recipe_mults = []
    
    # Alright, now we iterate through all of the entries
    # we added to the row list. For each one, we will calculate
    # it's x and y position based off of the row and column
    # that it occupies. Additionally, we'll add information about
    # attach points on the top and bottom of the icon, depending on 
    # the number of children that the icon has. Finally, we use
    # those attach points to populate the list of bezier curves
    # that we have to draw.     
    for depth, row in enumerate(recipe_list):
        filled_row_leaves = 0
        for entry in row:
            entry['top'] = depth * (ICON_HEIGHT + ROW_BUFFER)
            entry['left'] = (filled_row_leaves * ICON_WIDTH) + (ICON_WIDTH * entry['size']) / 2 - (ICON_WIDTH / 2)
            if depth != max_depth:
                # As long as we aren't at maximum depth (the bottom of the tree)
                # we proceed as if the entry has children, since we can't know
                # until we get to the next row.
                if 'mult' in entry:
                    # If we populated a mult entry, append it to the list of mults we must display.
                    recipe_mults.append({'mult': entry['mult'], 'position': (entry['left'] + ICON_WIDTH / 2, entry['top'] + ICON_HEIGHT + ROW_BUFFER / 2)})
                
                # Determine where to attach lines to the bottom of this icon. If there are
                # 0 bottom attach points, we fall through the ifelse, since we don't need
                # to do anything.             
                y_attach = entry['top'] + ICON_HEIGHT + BOTTOM_ATTACH_YBUFFER
                if entry['num_bottom_attach_points'] == 1:
                    entry['bottom_attach_points'] = [(entry['left'] + (ICON_WIDTH / 2), y_attach)]
                elif entry['num_bottom_attach_points'] > 1:
                    x_spacing = (ICON_WIDTH - (2*SIDE_ATTACH_XBUFFER)) / (entry['num_bottom_attach_points'] - 1)
                    entry['bottom_attach_points'] = []
                    for i in range(entry['num_bottom_attach_points']):
                        entry['bottom_attach_points'].append((entry['left'] + SIDE_ATTACH_XBUFFER + (i * x_spacing),y_attach))
            if depth != 0 and entry['good'] is not None:
                # Now, we need to draw lines to our parent. We don't do this if our good is None (meaning
                # we are a placeholder node populated during list created) or if we're at depth 0, which
                # is the top of the tree.
                entry['top_attach_point'] = (entry['left'] + (ICON_WIDTH / 2), entry['top'] - TOP_ATTACH_YBUFFER)
                parent = find_list_entry(filled_row_leaves, depth - 1)
                recipe_beziers.append(build_bezier((entry['top_attach_point'][0], entry['top_attach_point'][1], parent['bottom_attach_points'][0][0],parent['bottom_attach_points'][0][1])))
                parent['bottom_attach_points'] = parent['bottom_attach_points'][1:]
            filled_row_leaves += entry['size']
    
    td['recipe_list'] = recipe_list
    td['recipe_height'] = tree_height
    td['recipe_width'] = tree_width
    td['recipe_beziers'] = recipe_beziers
    td['recipe_mults'] = recipe_mults
    td['hash'] = hash
    
    return render_to_response('leapday/good.html', td, context_instance = RequestContext(request))
