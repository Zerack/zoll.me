'''
James D. Zoll
4/5/2013

Purpose: Defines application views for the Leap Day recipedia application.

License: This is a public work.

'''

import pprint
pp = pprint.PrettyPrinter(indent=2)
from math import sqrt

# Library Imports
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

# Local Imports
from leapday.models import Good

def index(request):
    goods = Good.objects.filter(num_ingredients__lte=5).exclude(key='good_other').order_by('-value').all()
    basic_goods = list(Good.objects.filter(good_type='goodtype_basic').order_by('value').all())
    basic_goods.append(Good.objects.filter(key='goodtype_crystal').get())
    basic_goods = basic_goods[1:]
    return render_to_response('leapday/index.html', {'goods': goods, 'basic_goods': basic_goods}, context_instance = RequestContext(request))

def good(request, key):

    def get_recipe_tree(g, g_depth=0):
        r = {'good': g}
        r_i = [x.ingredient for x in g.recipe_ingredients.all()]
        num_children = len(r_i)
        num_unique_children = len(set(r_i))
        
        if num_children > 0:
            # This is not a basic good.
            if num_children > 1 and num_unique_children == 1:
                # The recipe has only one type of good, and it takes more than one.
                r['children'] = [get_recipe_tree(r_i[0], g_depth+1)]
                r['children_mult'] = num_children
                r['leaves'] = r['children'][0]['leaves']
                r['depth'] = 1+ r['children'][0]['depth']
            else:
                # Standard recipe.
                r['children'] = [get_recipe_tree(x, g_depth+1) for x in r_i]
                r['leaves'] = sum(map(lambda x: x['leaves'], r['children']))
                r['depth'] = 1+ max(map(lambda x: x['depth'], r['children']))
        else:
            # Basic good.
            r['leaves'] = 1
            r['depth'] = 0
        return r
    
    def build_recipe_list(t, level, rl):
        rl[level].append({'good': t['good'], 'size': t['leaves'], 'num_bottom_attach_points': 0 if 'children' not in t else len(t['children'])})
        if 'children_mult' in t:
            rl[level][-1]['mult'] = t['children_mult']
        if 'children' in t:
            for child in t['children']:
                build_recipe_list(child, level + 1, rl)
        else:
            # If no children, we're either at max depth, or we need to insert
            # some dummies.
            if level < max_depth:
                build_recipe_list({'good': None, 'leaves': t['leaves']}, level + 1, rl)
        
        
    
    good_db = get_object_or_404(Good.objects.filter(key=key))
    
    ICON_WIDTH = 45
    ICON_HEIGHT = 54
    ROW_BUFFER = 20
    BOTTOM_ATTACH_YBUFFER = 3
    TOP_ATTACH_YBUFFER = -10
    SIDE_ATTACH_XBUFFER = ICON_WIDTH * 0.2
    
    recipe_tree = get_recipe_tree(good_db)
    print '\n\n'
    pp.pprint(recipe_tree)
    print '\n\n'
    
    leaves = recipe_tree['leaves']
    max_depth = recipe_tree['depth']
    
    tree_width = ICON_WIDTH * leaves
    tree_height = ICON_HEIGHT * (max_depth + 1) + (ROW_BUFFER * max_depth) 
    
    recipe_list = [[] for x in range(max_depth + 1)]
    build_recipe_list(recipe_tree, 0, recipe_list)
    
    recipe_lines = []
    recipe_mults = []
    
    def find_list_entry(x_pos, depth):
        filled_leaves = 0
        for i in recipe_list[depth]:
            item_start = filled_leaves
            item_end = filled_leaves + i['size']
            if item_start <= x_pos and x_pos < item_end:
                return i
            else:
                filled_leaves += i['size']
            
    
    for depth, row in enumerate(recipe_list):
        filled_row_leaves = 0
        for entry in row:
            entry['top'] = depth * (ICON_HEIGHT + ROW_BUFFER)
            entry['left'] = (filled_row_leaves * ICON_WIDTH) + (ICON_WIDTH * entry['size']) / 2 - (ICON_WIDTH / 2)
            if depth != max_depth:
                # handle extra multiplier for things like black oak, hammer, necklace, etc.
                # coordinates here are center of the thing.
                if 'mult' in entry:
                    recipe_mults.append({'mult': entry['mult'], 'position': (entry['left'] + ICON_WIDTH / 2, entry['top'] + ICON_HEIGHT + ROW_BUFFER / 2)})                
                y_attach = entry['top'] + ICON_HEIGHT + BOTTOM_ATTACH_YBUFFER
                if entry['num_bottom_attach_points'] == 1:
                    entry['bottom_attach_points'] = [(entry['left'] + (ICON_WIDTH / 2), y_attach)]
                elif entry['num_bottom_attach_points'] > 1:
                    x_spacing = (ICON_WIDTH - (2*SIDE_ATTACH_XBUFFER)) / (entry['num_bottom_attach_points'] - 1)
                    entry['bottom_attach_points'] = []
                    for i in range(entry['num_bottom_attach_points']):
                        entry['bottom_attach_points'].append((entry['left'] + SIDE_ATTACH_XBUFFER + (i * x_spacing),y_attach))
            if depth != 0 and entry['good'] is not None:
                entry['top_attach_point'] = (entry['left'] + (ICON_WIDTH / 2), entry['top'] - TOP_ATTACH_YBUFFER)
                parent = find_list_entry(filled_row_leaves, depth - 1)
                recipe_lines.append((entry['top_attach_point'][0], entry['top_attach_point'][1], parent['bottom_attach_points'][0][0],parent['bottom_attach_points'][0][1]))
                parent['bottom_attach_points'] = parent['bottom_attach_points'][1:]
            filled_row_leaves += entry['size']
            
            
    pp.pprint(recipe_list)
    print '\n\n'
    
    pp.pprint(recipe_mults)
    print '\n\n'
    
    def build_bezier(line):
        if line[0] == line[2]:
            x_increment = (line[2] - line[0]) / 3.0
            y_increment = (line[3] - line[1]) / 3.0
        
            line = (line[0],line[1],line[0]+x_increment, line[1] + y_increment, line[0]+ (2*x_increment), line[1]+(2*y_increment),line[2],line[3])
        else:
            line = (line[0], line[1], line[0], (line[3] + line[1]) / 2, line[2], (line[3] + line[1]) / 2, line[2], line[3])            
        return line
    
    recipe_beziers = []
    for line in recipe_lines:
        recipe_beziers.append(build_bezier(line))
        
        
    pp.pprint(recipe_beziers)
    print '\n\n'

    td = {'good': good_db,
          'recipe_list': recipe_list,
          'recipe_height': tree_height,
          'recipe_width': tree_width,
          'recipe_beziers': recipe_beziers,
          'recipe_mults': recipe_mults}
    
    return render_to_response('leapday/good.html', td, context_instance = RequestContext(request))