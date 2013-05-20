'''
James D. Zoll
4/5/2013

Purpose: Defines application views for the Leap Day recipedia application.

License: This is a public work.

'''

# Library Imports
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

# Local Imports
from leapday.models import Good, Recipe_Item, Base_Material

# Constants for the Goods page. Mostly for tree generation.
ICON_WIDTH = 47
ICON_HEIGHT = 58
ROW_BUFFER = 20
BOTTOM_ATTACH_YBUFFER = 3
TOP_ATTACH_YBUFFER = -10
SIDE_ATTACH_XBUFFER = ICON_WIDTH * 0.2

def index(request):    
    '''
    Returns the index page of the application, which shows the interactive
    list of recipes.
    
    '''
    
    # Grab the data. We have to do some gymnastics here since Django doesn't
    # support select_related() on reverse foreign keys at time of writing. So,
    # we'll manually fetch the objects we want in two queries, and stitch
    # them together manually. It's a bit gross, but it prevents 1400+ 
    # database hits. (Only 3 database hits)
    goods = Good.objects.filter(num_ingredients__lte=5).exclude(key='good_other').order_by('-value').all()
    obj_dict = dict([(obj.id, obj) for obj in goods])
    recipes = Recipe_Item.objects.select_related('ingredient').filter(product__in=goods).all()
    base_ingredients = Base_Material.objects.select_related('ingredient').filter(product__in=goods).all()
    
    recipe_relation_dict = {}
    for r in recipes:
        recipe_relation_dict.setdefault(r.product_id, []).append(r)
    for r_id, related_items in recipe_relation_dict.items():
        obj_dict[r_id].shim_recipe_ingredients = related_items
        
    base_relation_dict = {}
    for b in base_ingredients:
        base_relation_dict.setdefault(b.product_id, []).append(b)
    for b_id, related_items in base_relation_dict.items():
        obj_dict[b_id].shim_base_ingredients = related_items

    # Create the list of basic goods by filtering the appropriate stuff from
    # the goods object. Note that we would normally trim the "Other" good from
    # the beginning of this list, but it was excluded in the original query 
    # to Goods.
    basic_goods = sorted(filter(lambda x: x.good_type == 'goodtype_basic' or x.key=='goodtype_crystal', goods), key=lambda x: x.value)
    
    # All done. Pass it off to the templating engine.
    return render_to_response('leapday/index.html', {'goods': goods, 'basic_goods': basic_goods}, context_instance = RequestContext(request))

def good(request, key):
    '''
    Returns a page detailing information about the selected good. This includes
    icon, cost, flavor text, and production information. The majority of code
    in this view is dedicated to setting up the production web, which requires
    placing icons onto a canvas.
    
    Keyword Arguments:
    key -> String. The unique identifier for the good.
    
    '''
    
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
        #r_i = [x.ingredient for x in Recipe_Item.objects.filter(product=g).prefe_selected('ingredient').all()]
        r_i = [x.ingredient for x in g.recipe_ingredients.select_related('ingredient').all()]
        num_children = len(r_i)
        num_unique_children = len(set(r_i))
        
        # Depending on the relationship between the number of chidldren and
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
    
    # Initial database queries. We prefetch what we can to reduce overall database IO. 
    good = get_object_or_404(Good.objects.filter(key=key))
    ingredients = [x.ingredient for x in Recipe_Item.objects.select_related('ingredient').filter(product=good).all()]
    base_ingredients = sorted(Base_Material.objects.select_related('ingredient').filter(product=good).all(), key=lambda x: x.ingredient.value)
    base_ingredients = base_ingredients[1:] + [base_ingredients[0]]
    used_to_craft = sorted(list(set([x.product for x in Recipe_Item.objects.select_related('product').filter(ingredient=good).all()])), key=lambda x: x.value)
    
    # Fetch the recipe tree and store some information.
    recipe_tree = get_recipe_tree(good)
    
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
            
    # Everything has been prepared, so fill the template context object
    # and render the template.
    td = {'good': good,
          'ingredients': ingredients,
          'base_ingredients': base_ingredients,
          'used_to_craft': used_to_craft,
          'recipe_list': recipe_list,
          'recipe_height': tree_height,
          'recipe_width': tree_width,
          'recipe_beziers': recipe_beziers,
          'recipe_mults': recipe_mults}

    return render_to_response('leapday/good.html', td, context_instance = RequestContext(request))