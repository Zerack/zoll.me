''' 
James D. Zoll

4/8/2013

Purpose: Defines logic to parse and insert recipedia data into the database.

License: This is a public work.

'''
# System Imports
import sys

# Library Imports
from bs4 import BeautifulSoup

# Local Imports
from leapday.models import Good, Recipe_Item, Base_Material

def parse_good(g):
    '''
    Parses out all valid properties of the given good and returns
    a dictionary with the appropriate properties set.
    
    Keyword Arguments:
    g -> The good to parse.
    
    '''
    
    d = {}
    d['good_type'] = g.find(u'type')['value']
    d['key'] = g.find(u'key')['value'].lower()
    d['display_name'] = g.find(u'displayname')['value']
    d['tier'] = int(g.find(u'tier')['value'])
    try:
        d['base_multiplier'] = float(g.find(u'basemultiplier')['value'])
    except:
        d['base_multiplier'] = 0
    d['base_value'] = int(g.find(u'basevalue')['value'])
    d['num_ingredients'] = int(g.find(u'numingredients')['value'])
    d['recipe_value_multiplier'] = float(g.find(u'recipevaluemultiplier')['value'])
    d['value'] = int(g.find(u'value')['value'])
    d['description'] = g.find(u'description')['value']
    active = True if g.find(u'active')['value'] == u'TRUE' else False
    ingredients = [x['value'].lower() for x in g.find(u'craftingrecipe').find_all('good')]
    return d, ingredients, active

# First, empty the table.
Good.objects.all().delete()
print 'Cleaned table LEADPDAY_GOOD.'

# Next, add a fake "Other" good to the table. This is used in a variety of recipes.
good_other = Good(key='good_other',good_type='goodtype_basic',display_name='Other',tier=1,base_multiplier=0,
                  base_value=0,num_ingredients=0,recipe_value_multiplier=0,
                  value=0,description='Anything that does not satisfy a more valuable recipe.')
good_other.save()
good_other_bm = Base_Material(product=good_other, ingredient=good_other, quantity=1)
good_other_bm.save()
print 'Added fake "Other" item entry.'

# Initialize a null goodtype_crystal entry.
goodtype_crystal = None

# Now, open up the XML file and make a beautiful soup object from it.
with open('config_20130627.xml','r') as config_xml:
    bs = BeautifulSoup(config_xml.read())
print 'Read CONFIG.XML.'

# We're going to iterate through all of the goods, building the tree
# of recipes as we go. This requires going through the loop carefully
# (perhaps more than once) to make sure everything has appropriate children
# when required.
#
# There are a few other special cases we have to care about when building data.
# 1) The generic "Crystal" good that is used in all recipes requiring crystals
#    has goodtype "good_crafted' and key 'goodtype_crystal'. This requires
#    some special parsing.
# 2) The recipe 'Junk' shows up as 'goodtype_basic', even though it's technically
#    the result of crafting, and has a recipe (3 "Other"). This needs to be handled
#    separately.
# 3) There are some recipes with > 5 items, which at time of writing is not possible
#    in game. These should be ignored.
goods = bs.find(u'goods').find_all('good', recursive=False)
print 'Found {0} Goods. Parsing Now.'.format(len(goods))
idx = 0
loop_check = False
while len(goods) > 0:
    cg, cg_ingredients, cg_active = parse_good(goods[idx])
    print '\nProcessing good at index {0}, "{1}"'.format(idx, cg['display_name'])
    if not cg_active:
        # If the good is inactive, skip it and remove it from the list.
        print 'Inactive good detected. Skipping.'
        goods = goods[:idx] + goods[idx+1:]
        loop_check = True
    elif cg['good_type'] == u'goodtype_basic' and cg['key'] != u'good_junk':
        # If this is a basic good, we will create a record, and then add the single base material information required.
        print 'Basic good detected. Adding Good object.'
        cg_db = Good(**cg)
        cg_db.save()
        
        print 'Good object added. Adding Base_Material object.'
        cgbm_db = Base_Material(product=cg_db, ingredient=cg_db, quantity=1)
        cgbm_db.save()
        
        print 'Base_Material object added. Removing {0} from outstanding goods list.'.format(cg['display_name'])
        goods = goods[:idx] + goods[idx+1:]
        loop_check = True
    elif cg['good_type'] == u'goodtype_crystal':
        # If this is a crystal good, we will do almost exactly the same thing, but the base material
        # entry will have the generic crystal instead of the type specific one. This requires that this 
        # variable has been parsed.
        if goodtype_crystal is None:
            print 'Crystal good detected. GOODTYPE_CRYSTAL not yet parsed. Skipping.'
            idx += 1
        else:
            print 'Crystal good detected. GOODTYPE_CRYSTAL is defined. Adding Good object.'
            cg_db = Good(**cg)
            cg_db.save()
            
            print 'Good object added. Adding Base_Material object.'
            cgbm_db = Base_Material(product=cg_db, ingredient=goodtype_crystal, quantity=1)
            cgbm_db.save()
            
            print 'Base_Material object added. Removing {0} from outstanding goods list.'.format(cg['display_name'])
            goods = goods[:idx] + goods[idx+1:]
            loop_check = True
    elif cg['key'] == u'goodtype_crystal':
        # If we detected the goodtype_crystal unique case, it's mostly the same,
        # except that we populate the base goodtype_crystal variable.
        print 'GOODTYPE_CRYSTAL detected. Adding Good object.'
        cg['description'] = 'Crystals used to craft shiny objects. Recipes requiring Crystal are only satisfied if each crystal is a different type.'  
        goodtype_crystal = Good(**cg)
        goodtype_crystal.save()
        
        print 'Good object added. Adding Base_Material object.'
        cgbm_db = Base_Material(product=goodtype_crystal, ingredient=goodtype_crystal, quantity=1)
        cgbm_db.save()
        
        print 'Base_Material object added. Removing {0} from outstanding goods list.'.format(cg['display_name'])
        goods = goods[:idx] + goods[idx+1:]
        loop_check = True
    elif cg['key'] == u'good_junk':
        # The junk craftable is interesting, because we need to also
        # populate a recipe for the item.
        print 'JUNK detected. Adding Good object.'
        cg['good_type'] = 'goodtype_crafted'    
        cg_db = Good(**cg)
        cg_db.save()
        
        print 'Good object added. Adding Base_Material object.'
        cgbm_db = Base_Material(product=cg_db, ingredient=good_other, quantity=2)
        cgbm_db.save()
        
        print 'Base_Material object added. Adding Recipe_Item objects.'
        for i in range(2):
            cg_recipe_item = Recipe_Item(product=cg_db, ingredient=good_other, display_order=i)
            cg_recipe_item.save()
        
        print 'Recipe_Item objects added. Removing {0} from outstanding goods list.'.format(cg['display_name'])
        goods = goods[:idx] + goods[idx+1:]
        loop_check = True
    elif cg['good_type'] == u'goodtype_crafted':
        # This is the general case for a craftable item. We add the item to the database,
        # then the recipe. After that, we count the total required items and add the Base_Material
        # counts as required. 
        #
        # Note: This can all only happen if all of the ingredients have already been parsed. If they
        #       haven't, we skip around and do them next time. 
        print 'Crafted item detected. Checking database for ingredients.'
        ingredients_db = Good.objects.filter(key__in=cg_ingredients).all()
        if set(cg_ingredients) != set([x.key for x in ingredients_db]):
            print 'Some ingredients for this recipe have not yet been parsed. Skipping'
            print 'Required: {0}'.format(', '.join(cg_ingredients))
            print 'Found: {0}'.format(', '.join([x.display_name for x in ingredients_db]))
            idx += 1
        else:
            print 'All ingredients are present. Adding Good object.'
            cg_db = Good(**cg)
            cg_db.save()
            
            print 'Good object added. Adding Recipe_Item objects.'
            
            '''
            Removed 5/20/2013
            All recipes have exactly the correct number of items. No ?'s are needed.
            
            ==============
            
            if len(cg_ingredients) <= 3:
                cg_ingredients += ['good_other'] * (3 - len(cg_ingredients))
            elif len(cg_ingredients) <= 5:
                cg_ingredients += ['good_other'] * (5 - len(cg_ingredients))
                
            ==============
            '''                
                
            ingredients_db = list(ingredients_db) + [good_other]
            
            bm = {}
            for i, ingredient in enumerate(cg_ingredients):
                ingredient_db = filter(lambda x: x.key == ingredient, ingredients_db)[0]
                
                cg_recipe_item = Recipe_Item(product=cg_db, ingredient=ingredient_db, display_order=i)
                cg_recipe_item.save()
                
                for ingredient_base in ingredient_db.base_ingredients.all():
                    if ingredient_base.ingredient not in bm:
                        bm[ingredient_base.ingredient] = 0
                    bm[ingredient_base.ingredient] += ingredient_base.quantity            
            
            print 'Good object added. Adding Base_Material objects.'
            for key, value in bm.iteritems():         
                cgbm_db = Base_Material(product=cg_db, ingredient=key, quantity=value)
                cgbm_db.save()
            
            print 'Base_Material object added. Removing {0} from outstanding goods list.'.format(cg['display_name'])
            goods = goods[:idx] + goods[idx+1:]  
            loop_check = True
    else:
        print 'WARNING: Unexpected entry format. Failing!'
        break
    
    # At this point, we loop around. However, if idx is out of bounds, reset it to 0. Additionally,
    # we set the loop_ch
    if idx >= len(goods):
        if not loop_check:
            print '\nWARNING: Infinite loop detected! Failing!\n'
            sys.exit()
        else:
            print '\nGoods exhausted. Returning to top of list.\n'
            loop_check = False
            idx = 0

print 'Parsing complete. Finalizing base material counts.'

# Alright, the last thing that we have to do is to go through every item and add the 
# 0s in for base materials that aren't used. This can't be done while we parse the first time
# since we can never know when we've actually parsed all of the base materials.
#
# There is one special case here. We take all 'goodtype_basic' items, plus the key='goodtype_crystal'
# basic type.
goods_base = list(Good.objects.filter(good_type='goodtype_basic').all())
goods_base.append(Good.objects.filter(key='goodtype_crystal').get())
goods_base = set(goods_base)
for good in Good.objects.all():
    present_base = set([x.ingredient for x in good.base_ingredients.all()])
    print '\n'
    print goods_base
    print present_base
    print goods_base - present_base
    for missing_base in list(goods_base - present_base):
        cgbm_db = Base_Material(product=good, ingredient=missing_base, quantity=0)
        cgbm_db.save()
        
print 'Base material counts complete.'

print 'Operation Complete!'
            