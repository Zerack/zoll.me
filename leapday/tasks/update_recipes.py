''' 
James D. Zoll

4/8/2013

Purpose: Defines logic to parse and insert recipedia data into the database.

License: This is a public work.

'''
# System Imports
import sys
from urllib import urlopen

# Library Imports
from bs4 import BeautifulSoup

# Local Imports
from leapday.models import Good, Recipe_Item, Base_Material

# Constants and Configuration
XML_URL = 'http://sparkypants.com/LeapDayGoods.xml'
NUM_FETCH_TRIES = 3
CRYSTAL_DESCRIPTION = ('Crystals used to craft shiny objects. ' + 
                       'Recipes requiring Crystal are only ' + 
                       'satisfied if each crystal is a ' + 
                       'different type.')

def GEN_GOOD_OTHER():
    '''
    Creates a database object that is representative of the "Other" good,
    a good used when a recipe allows a wildcard item.
    
    '''
    
    return Good(key='good_other',good_type='goodtype_basic',
                display_name='Other',tier=1,base_multiplier=0,
                base_value=0,num_ingredients=0,recipe_value_multiplier=0,
                value=0,description=('Anything that does not satisfy ' + 
                                     'a more valuable recipe.'))

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
    d['recipe_value_multiplier'] = float(g.find
                                         (u'recipevaluemultiplier')['value'])
    d['value'] = int(g.find(u'value')['value'])
    d['description'] = g.find(u'description')['value']
    active = True if g.find(u'active')['value'] == u'TRUE' else False
    ingredients = [x['value'].lower() for x in g.find(u'craftingrecipe')
                   .find_all('good')]
    return d, active, ingredients

def update_recipes(out=None):
    '''
    Controls the process to update recipes in an automated fashion.
    Generally, will update prices or crafting requirements changes
    with no intervention. If a new good is added, the update will
    abort with log messages indicated that new images need to be
    parsed out.
    
    Keyword Arguments:
    out -> The stream to use as stdout.
    
    '''
    
    # If out wasn't given, use stdout
    if out is None:
        out = sys.stdout
        
    # Alright, fetch the most up to date XML from the web.
    out.write('Fetching current XML from "{0}".'.format(XML_URL))
    soup = None
    for i in xrange(NUM_FETCH_TRIES):
        try:
            soup = BeautifulSoup(urlopen(XML_URL).read())
            break
        except:
            exc_info = sys.exc_info()
            
    if soup is None:
        out.write('Error fetching current XML. Aborting recipe update.')
        out.write(str(exc_info()[1]))
        return
    out.write('XML fetched successfully.')
    
    # We will now parse each of the goods and store them in a dictionary by
    # their "key_value" field. We have to do this regardless of whether we
    # end up inserting new data or not, so it's alright to do this now.
    goods_list = map(lambda x: parse_good(x), 
                     soup.find(u'goods').find_all('good', recursive=False))
    
    # So, now we need to check to see if new items were added. We will select
    # from out existing database, and expect that there will already be an
    # item for each that currently exists. It is alright if an item was removed,
    # as we can deal with that without issue. 
    out.write('Validating fetched item list against existing database.')
    try:
        existing_count = Good.objects.filter(key__in=map(lambda x: x[0]['key'], 
                                                        goods_list)).all()
    except:
        out.write('Error checking against existing items. Aborting update.')
        out.write(str(sys.exc_info()[1]))
        return
    
    if existing_count < len(goods_list):
        out.write('There appears to be a new item. Manual action is ' +
                  'required. Aborting recipe update.')
        return
    out.write('New item list appears to be valid. Continuing with update.')
    
    # OK, so we think we're good to go as far as items, so we can proceed
    # with the update. We will begin by clearing the existing data and 
    # then inserting the fake "Other" object, which is needed in case a 
    # recipe refers to it.
    out.write('Cleaning table LEAPDAY_GOOD')
    try:
        Good.objects.all().delete()
    except:
        out.write('Error cleaning existing LEAPDAY_GOOD table. Aborting ' +
                  'recipe update.')
        out.write(str(sys.exc_info()[1]))
    out.write('LEAPDAY_GOODS table cleaned.')
    
    out.write('Adding "Other" Good to goods list.')
    try:
        good_other = GEN_GOOD_OTHER()
        good_other.save()
        good_other_bm = Base_Material(product=good_other, ingredient=good_other, 
                                      quantity=1)
        good_other_bm.save()
    except:
        out.write('Error added "Other" good to goods list. Aborting recipe ' + 
                  'update.')
        out.write(str(sys.exc_info()[1]))
    out.write('"Other" good added successfully.')
    
    # A little housekeeping - we have to initialize the goodtype_crystal entry
    # to None, so that we can check specific recipes to see if it has been found
    # yet. We know it will exist somewhere, but we have to bootstrap it here
    # to make things work.
    goodtype_crystal = None
    
    # We're ready to loop through the goods. Because they are not guaranteed
    # to be in hierarchical order, we have to allow multiple passes through
    # the loop. We'll keep track of our index in the loop, as well as a check
    # variable that will throw an error if we make a full pass through our list
    # without finding anything to insert.
    idx = 0
    modified_list = False
    
    # There are a few special cases we have to care about when building data.
    # 1) The generic 'Crystal' good that is used in all recipes requiring
    #    crystals has goodtype "good_crafted" and key "goodtype_crystal". This
    #    requires a little extra handling, since it doesn't have a recipe
    #    even though the XML treats it as a crafted good.
    # 2) The recipe "Junk" shows up as 'goodtype_basic', even though it's 
    #    technically a crafted item, and has a recipe of 2 "Other" items. This
    #    needs to be handled in a special case.
    out.write('Beginning Goods processing. ' + 
              'There are {0} goods to process'.format(len(goods_list)))
    while len(goods_list) > 0:
        cg, cg_active, cg_ingredients = goods_list[idx]
        out.write('..Processing good at ' + 
                  'index {0}, "{1}"'.format(idx, cg['display_name']))
        
        if not cg_active:
            # If the good is inactive, skip it and remove it from the list.
            out.write('....Inactive good detected. Skipping.')
            goods_list = goods_list[:idx] + goods_list[idx+1:]
            modified_list = True
        elif cg['good_type'] == u'goodtype_basic' and cg['key'] != u'good_junk':
            # If this is a basic good, we will create a record, and then add the
            # single base material information required.
            out.write('....Basic good detected. Adding Good object.')
            cg_db = Good(**cg)
            cg_db.save()
            
            out.write('....Good object added. Adding Base_Material object.')
            cgbm_db = Base_Material(product=cg_db, ingredient=cg_db, quantity=1)
            cgbm_db.save()
            
            out.write(('....Base_Material object added. Removing {0} from ' + 
                       'outstanding goods list.').format(cg['display_name']))
            goods_list = goods_list[:idx] + goods_list[idx+1:]
            modified_list = True
        elif cg['good_type'] == u'goodtype_crystal':
            # If this is a crystal good, we will do almost exactly the same
            # thing, but the base material entry will have the generic crystal
            # instead of the type specific one. This requires that this variable
            # has been parsed.
            if goodtype_crystal is None:
                out.write('....Crystal good detected. GOODTYPE_CRYSTAL not ' + 
                          'yet parsed. Skipping.')
                idx += 1
            else:
                out.write('....Crystal good detected. GOODTYPE_CRYSTAL is ' + 
                          'defined. Adding Good object.')
                cg_db = Good(**cg)
                cg_db.save()
                
                out.write('....Good object added. Adding Base_Material object.')
                cgbm_db = Base_Material(product=cg_db, 
                                        ingredient=goodtype_crystal, quantity=1)
                cgbm_db.save()
                
                out.write(('....Base_Material object added. ' +
                           'Removing {0} from ' + 
                          'outstanding goods list.').format(cg['display_name']))
                goods_list = goods_list[:idx] + goods_list[idx+1:]
                modified_list = True
        elif cg['key'] == u'goodtype_crystal':
            # If we detected the goodtype_crystal unique case, it's mostly the 
            # same, except that we populate the base goodtype_crystal variable.
            out.write('....GOODTYPE_CRYSTAL detected. Adding Good object.')
            cg['description'] = CRYSTAL_DESCRIPTION  
            goodtype_crystal = Good(**cg)
            goodtype_crystal.save()
            
            out.write('....Good object added. Adding Base_Material object.')
            cgbm_db = Base_Material(product=goodtype_crystal,
                                    ingredient=goodtype_crystal, quantity=1)
            cgbm_db.save()
            
            out.write(('....Base_Material object added. Removing {0} from ' + 
                       'outstanding goods list.').format(cg['display_name']))
            goods_list = goods_list[:idx] + goods_list[idx+1:]
            modified_list = True
        elif cg['key'] == u'good_junk':
            # The junk craftable is interesting, because we need to also
            # populate a recipe for the item.
            out.write('....JUNK detected. Adding Good object.')
            cg['good_type'] = 'goodtype_crafted'    
            cg_db = Good(**cg)
            cg_db.save()
            
            out.write('....Good object added. Adding Base_Material object.')
            cgbm_db = Base_Material(product=cg_db, 
                                    ingredient=good_other, quantity=2)
            cgbm_db.save()
            
            out.write('....Base_Material object added. Adding Recipe_Item ' + 
                      'objects.')
            for i in range(2):
                cg_recipe_item = Recipe_Item(product=cg_db, 
                                             ingredient=good_other, 
                                             display_order=i)
                cg_recipe_item.save()
            
            out.write(('....Recipe_Item objects added. Removing {0} from ' + 
                       'outstanding goods list.').format(cg['display_name']))
            goods_list = goods_list[:idx] + goods_list[idx+1:]
            modified_list = True
        elif cg['good_type'] == u'goodtype_crafted':
            # This is the general case for a craftable item. We add the item to
            # the database, then the recipe. After that, we count the total
            # required items and add the Base_Material counts as required. 
            #
            # Note: This can all only happen if all of the ingredients have
            #       already been parsed. If they haven't, we skip around and do
            #       them next time. 
            out.write('....Crafted item detected. Checking database for ' + 
                      'ingredients.')
            ingredients_db = Good.objects.filter(key__in=cg_ingredients).all()
            if set(cg_ingredients) != set([x.key for x in ingredients_db]):
                out.write('....Some ingredients for this recipe have not yet ' +
                          'been parsed. Skipping')
                out.write('....Required: {0}'.format(', '.join(cg_ingredients)))
                out.write(('....Found: ' +
                           '{0}').format(', '.join([x.display_name
                                                    for x in ingredients_db])))
                idx += 1
            else:
                out.write('....All ingredients are present. Adding Good ' + 
                          'object.')
                cg_db = Good(**cg)
                cg_db.save()                
                out.write('....Good object added. Adding Recipe_Item objects.')              
                    
                ingredients_db = list(ingredients_db) + [good_other]
                
                bm = {}
                for i, ingredient in enumerate(cg_ingredients):
                    ingredient_db = filter(lambda x: x.key == ingredient, 
                                           ingredients_db)[0]
                    
                    cg_recipe_item = Recipe_Item(product=cg_db, 
                                                 ingredient=ingredient_db, 
                                                 display_order=i)
                    cg_recipe_item.save()
                    
                    for i_base in ingredient_db.base_ingredients.all():
                        if i_base.ingredient not in bm:
                            bm[i_base.ingredient] = 0
                        bm[i_base.ingredient] += i_base.quantity            
                
                out.write('....Good object added. Adding Base_Material ' +
                          'objects.')
                for key, value in bm.iteritems():         
                    cgbm_db = Base_Material(product=cg_db, ingredient=key, 
                                            quantity=value)
                    cgbm_db.save()
                
                out.write(('....Base_Material object added. ' +
                           'Removing {0} from ' +
                          'outstanding goods list.').format(cg['display_name']))
                goods_list = goods_list[:idx] + goods_list[idx+1:]  
                modified_list = True
        else:
            out.write('\nERROR: Unexpected entry format. Aborting update.\n')
            return
        
        # At this point, we loop around. However, if idx is out of bounds, 
        # reset it to 0. Additionally, we set the modified_list back to false,
        # since we're going back to the beginning.
        if idx >= len(goods_list):
            if not modified_list:
                out.write('\nWARNING: Infinite loop detected! Failing!\n')
                return
            else:
                out.write('..Goods exhausted. Returning to top of list.')
                modified_list = False
                idx = 0
    
    out.write('Goods parsing complete.')

    # Alright, the last thing that we have to do is to go through every item and
    # add the 0s in for base materials that aren't used. This can't be done
    # while we parse the first time since we can never know when we've actually
    # parsed all of the base materials.
    #
    # There is one special case here. We take all 'goodtype_basic' items, plus
    # the key='goodtype_crystal' basic type.
    out.write('Finalizing Base Material counts.')
    try:
        goods_base = list(Good.objects.filter(good_type='goodtype_basic').all())
        goods_base.append(Good.objects.filter(key='goodtype_crystal').get())
        goods_base = set(goods_base)
    except:
        out.write('Error fetching base goods from database. Aborting update.')
        out.write(str(sys.exc_info()[1]))
        return
    out.write('Fetched base goods from database.')
    
    out.write('Fetching all Goods objects from database.')
    try:
        goods_db = Good.objects.all()
    except:
        out.write('Error fetching all Goods objects from database. ' +
                  'Aborting update.')
        out.write(str(sys.exc_info()[1]))
        return
    out.write('Fetched all Goods objects from database.')
        
    for good in goods_db:
        present_base = set([x.ingredient for x in good.base_ingredients.all()])
        out.write('..Processing missing base ingredients ' +
                  '(if any) for "{0}".'.format(good.display_name))
        for missing_base in list(goods_base - present_base):
            try:
                cgbm_db = Base_Material(product=good, ingredient=missing_base, 
                                        quantity=0)
                cgbm_db.save()
            except:
                out.write('Error adding base material record for ' +
                          'missing base material. Aborting update.')
                out.write(str(sys.exc_info()[1]))
                return
    out.write('Finished finalizing base material counts.')
    out.write('\nRecipe Update Complete.\n')
    
# We'd like to be able to invoke this manually.
if __name__ == '__main__':
    update_recipes()

            