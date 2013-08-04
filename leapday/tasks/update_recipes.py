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
from leapday.models import Good

# Constants and Configuration
XML_URL = 'http://sparkypants.com/LeapDayGoods.xml'
NUM_FETCH_TRIES = 3
CRYSTAL_DESCRIPTION = ('Crystals used to craft shiny objects. ' + 
                       'Recipes requiring Crystal are only ' + 
                       'satisfied if each crystal is a ' + 
                       'different type.')

def parse_good(g):
    '''
    Parses out all valid properties of the given good and returns
    a dictionary with the appropriate properties set.
    
    Keyword Arguments:
    g -> The good to parse.
    
    '''
    
    d = {}
    
    d['active'] = True if g.find(u'active')['value'] == u'TRUE' else False
    d['key'] = g.find(u'key')['value'].lower()
    try:
        d['level'] = int(g.find(u'level')['value'])
    except TypeError:
        pass
    try:
        d['sub_key'] = g.find(u'subkey')['value'].lower()
    except TypeError:
        pass
    d['shopkeeper'] = g.find(u'shopkeeper')['value']
    d['occupation'] = g.find(u'occupation')['value']
    try:
        d['base_multiplier'] = float(g.find(u'basemultiplier')['value'])
    except TypeError:
        pass
    d['base_value'] = float(g.find(u'basevalue')['value'])
    d['num_ingredients'] = int(g.find(u'numingredients')['value'])
    d['recipe_value_multiplier'] = float(g.find
                                         (u'recipevaluemultiplier')['value'])
    d['value'] = int(g.find(u'value')['value'])
    d['ingredients'] = [x['value'].lower() for x in g.find(u'craftingrecipe')
                        .find_all('good')]
    d['used_in_other_recipes'] = int(g.find(u'usedinotherrecipes')['value'])
    d['allow_junk'] = True if g.find(u'allowjunk')['value'] == u'TRUE' else False
    
    # Shimmed in for now!!
    try:
        d['display_name'] = KEY_DISPLAY_NAMES[d['key']]
        d['description'] = KEY_DESCRIPTIONS[d['key']]
    except:
        d['display_name'] = 'UNKNOWN - ' + d['key']
        d['description'] = 'placeholder'
    
    return d

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
        out.write(str(exc_info[1]))
        return
    out.write('XML fetched successfully.')
    
    # We will now parse each of the goods and store them in a dictionary by
    # their "key_value" field. We have to do this regardless of whether we
    # end up inserting new data or not, so it's alright to do this now.
    goods_list = map(lambda x: parse_good(x), 
                     soup.find(u'goods').find_all('good', recursive=False))
    
    # OK, so we think we're good to go as far as items, so we can proceed
    # with the update. We will begin by clearing the existing data.
    out.write('Cleaning table LEAPDAY_GOOD')
    try:
        Good.objects.all().delete()
    except:
        out.write('Error cleaning existing LEAPDAY_GOOD table. Aborting ' +
                  'recipe update.')
        out.write(str(sys.exc_info()[1]))
    out.write('LEAPDAY_GOODS table cleaned.')
    
    # Since we don't build base material counts on the fly anymore, we
    # can just loop through and add everything. Perhaps later some more
    # validation should be added to this process, eh?
    out.write('Beginning Goods processing. ' + 
              'There are {0} goods to process'.format(len(goods_list)))
    for cg in goods_list:
        out.write('..Processing good "{0}"'.format(cg['display_name']))
        
        if not cg['active']:
            # If the good is inactive, skip it and remove it from the list.
            out.write('....Inactive good detected. Skipping.')
        elif len(cg['ingredients']) == 0:
            # If this is a basic good, we will create a record, and then add the
            # single base material information required.
            out.write('....Basic good detected. Adding Good object.')
            cg_db = Good(key=cg['key'], display_name=cg['display_name'],
                         base_value=cg['base_value'],
                         description=cg['description'])
            cg_db.save()
            
            out.write('....Good object added.')
        else:
            # This is the general case for a craftable item. We add the item to
            # the database, then the recipe. After that, we count the total
            # required items and add the Base_Material counts as required. 
            #
            # Note: This can all only happen if all of the ingredients have
            #       already been parsed. If they haven't, we skip around and do
            #       them next time. 
            out.write('....Crafted item detected.')
            cg_db = Good(key=cg['key'], level=cg['level'],
                         display_name=cg['display_name'],
                         multiplier=cg['recipe_value_multiplier'],
                         num_ingredients=cg['num_ingredients'],
                         description=cg['description'],
                         shopkeeper=cg['shopkeeper'],
                         occupation=cg['occupation'],
                         ingredient_0=cg['ingredients'][0] if len(cg['ingredients']) > 0 else None,
                         ingredient_1=cg['ingredients'][1] if len(cg['ingredients']) > 1 else None,
                         ingredient_2=cg['ingredients'][2] if len(cg['ingredients']) > 2 else None,
                         ingredient_3=cg['ingredients'][3] if len(cg['ingredients']) > 3 else None,
                         ingredient_4=cg['ingredients'][4] if len(cg['ingredients']) > 4 else None,)
            cg_db.save()                
            out.write('....Good object added. ')              

# SHIM FOR DESCRIPTIONS
KEY_DESCRIPTIONS = {
'good_food':'A bulbous protein rich berry.  Clever monkeys can cook it into almost any yummy delicacy.',
'good_wood':'Once, the living trunk of a majestic tree.  Now dead.',
'good_water':'Cool clear pond water.  Scum free!',
'good_stone':'Rough stone from a local mountain.',
'good_barrel':'Stout and full of water. You can shoot fish in it.',
'good_oak':'A hard wood that has lived a hard life.  Misses its baby acorns.',
'good_bread':'Fresh, hot loafs right out of the oven.  Try slices dribbled with honey and melted butter.',
'good_bricks':'The finest red clay bricks this side of Greater Flandon.',
'good_spirits':'Distilled berries yield a harsh liquor that puts hair in places you really don\'t want hair.',
'good_lumber':'Planks hand-planed by an elderly master craftsman.  Each wood shaving is so fine you can see the sunset shine through.',
'good_perfume':'Dab a little of this under your chin and the flan come runnin\'',
'good_gems':'Sparkly bits of glitter cut with a water wheel.',
'good_stew':'Savory stew made from roots, sausage and your mother\'s soupy secrets. The steam fogs your glasses.',
'good_ore':'Fractured stone under great heat reveals a metallic core. Ore! Go forth and forge a vast industry!',
'good_spices':'The nubby petals, when ground in a Flannish mortar, produce a red powder that sets the senses aflame.',
'good_glass':'Twelve parts sand, three parts trona, two parts lime. Brought to a bubble and then made into church windows.',
'good_cookedfood':'The home cooked meal you miss so much.',
'good_flour':'A white fruit-based flour used for baking.  Also fun to jump into and pretend you are a ghost.',
'good_mana':'Food of the gods.  The gods unfortunately were machines, so consuming mana tends to make one\'s tongue blister.',
'good_mulledwine':'An intoxicating staple of winter nights spent with friends \'round a table full of food and song.',
'good_shrines':'Items of worship mass produced for mass.',
'good_potionofdeath':'A poisonous beverage favored by ex-lovers and spiteful goldfish owners.',
'good_potionofjoy':'Love in a bottle.  Sold in bulk to certified therapists.',
'good_potionoflife':'Each flask contains a guaranteed five additional minutes of life.  Drink slowly to avoid exploding.',
'good_jewelry':'These baubles cling to the curve of your breast.',
'good_idols':'Small statuettes that contain a false bottom for hiding sacrilegious items.',
'good_gunpowder':'A black powder used in fireworks and other celebratory activities. Like the upcoming purge of the Queen\'s enemies.',
'goodtype_crystal':'Crystals used to craft shiny objects. Recipes requiring Crystal are only satisfied if each crystal is a different type.',
'good_onyx':'A banded variety of chalcedony.  Ha! You are now smarter than your brother.',
'good_jade':'A green stone that reminds this scholar of your aunt\'s eyes on that summer dawn.',
'good_opal':'A shimmering gem of many colors.  This one happens to be of the rare non-Australian variety',
'good_amber':'Fossilized sap. Occasionally pieces contain dead bugs and eternal memories.',
'good_silver':'A metal that is deeply jealous of gold and all the love it gets.  Sometimes found crying itself to sleep.',
'good_diamond':'Diamonds are what happens when you squeeze a tree really tightly. Quite rare due to the Purge of the Tree Squeezers in 40 AD.',
'good_sapphire':'A diamond dipped in blue dye',
'good_ruby':'Long ago jewelers sacrificed miniature goats to turn stones red. If you hold a ruby up to your ear, you just might be able to hear the bleating.',
'good_amethyst':'No one likes amethyst.',
'good_rings':'A band wrought of precious materials.  It speaks of a promise not always kept.',
'good_necklace':'Necklaces are armor that lay bare our humdrum visage when removed.  Invaluable.',
'good_shields':'A polished shield perfect for hanging on walls in order to pretend that you are manly.',
'good_hammers':'Long of shaft and thick of head, these are not intended to be used on drums. The drum maker is very angry.',
'good_largebarrel':'When a standard sized barrel just isn\'t enough.',
'good_blackoak':'The oak preferred by pirates and brigands.',
'good_blackbread':'A dense loaf traditionally consumed by soaking in stout',
'good_firedbricks':'An upscale brick for rich folks that look down on red bricks as plebian.',
'good_whiskey':'Aged to maturity in artisanal black oak barrels, a single sip will burn your socks off.',
'good_chair':'Have a seat.',
'good_jewelrybox':'The lock on the intricate box promises more than the costume jewelry.',
'good_desk':'This classic desk was popularized in the Elder Puddingham era.  No assembly required because flan are not (and never will be) Swedish.',
'good_incense':'Legalized in three states',
'good_rockhammers':'Hammer for bashing rock. Used by the workers to the east that lost their jobs and families to the illness with no cure.',
'good_beer':'A well hopped ale',
'good_fruitcake':'Sometimes we give bad gifts because we care too much to give fragile feeling form.',
'good_cinnamonrolls':'My fingers are so sticky. Are your fingers sticky too?  Even If you lick them, they don\'t stop being sticky.',
'good_catstatue':'This was once a real cat, but then it was soaked in a special varnish. Now you can pet Fluffy forever.',
'good_metalingot':'The poor sell their fillings to be melted into ingots',
'good_curry':'\'The only way to enjoy spicy food is on the way in\' -Flannish proverb',
'good_chowder':'This was the meal that the fisherman ate the night before he was lost at sea.',
'good_grog':'A seafarer\'s concoction made of weak beer, rum and a dash of lemon to chase off the scurvy.',
'good_chili':'A hearty southern meal made from beans and locals that did not pay their royal taxes.',
'good_windows':'An outdated product whose rudderless inventor is likely to go bankrupt in the next decade.',
'good_spyglass':'In a well ordered society, it is a neighbor\'s duty to report unseemly details with great gusto.  The spyglass is merely a facilitator.',
'good_finebrandy':'Now that cigars are banned in public places, consumption of brandy has doubled.',
'good_crockpot':'All good moments in life can be slowly stewed in a crockpot.  Lift the lid, inhale and remember everything.',
'good_lembascakes':'An English crisp.',
'good_luxuryfood':'The sort of plated meal a well off bachelor orders when attempting to impress an ingenue',
'good_glue':'Sniffless and extremely capable of non-emotional bonding.',
'good_firebread':'Baked by lighting a tiny fire inside a bread crust cavity.  Eaten by families on Saturday nights.',
'good_fineflour':'When cooking pastries only the silkiest baking flour will prevent the chef from smacking you and yelling \'Dolt!\'',
'good_sweetwine':'Wine bewitched with the sweet tears of mispent youth.',
'good_rowboat':'\'This stealthy rowboat is surprisingly useful if you need to get rid of a body.\' Sales brochure, selling point #3.',
'good_haircream':'The simple fact that you do not possess this amazing hair-styling product explains everything that has gone wrong with your life.',
'good_firering':'A ring of fire.  It burns, burns, burns.',
'good_poisonring':'When slipped upon a finger, a single twist releases a venom that makes you appear dead for 12 hours.',
'good_stonering':'The sort of thing an insecure man wears in order to pretend that they aren\'t wearing jewelry.',
'good_firenecklace':'Traditional dress of the high governors that stoke the fire tower flames.',
'good_poisonnecklace':'All you need to do is hug your victim.  Please observe that the needles face outward.',
'good_stonenecklace':'Recommended fashion for thick necked individuals with sloping shoulders.',
'good_crystalshield':'A shield you can hide behind and still see where you are going.  Two handed',
'good_spiritshield':'A shield imbued with expensive cantrips to block the ghost of your mother from seeing what you are doing with your life.',
'good_stealthshield':'This shield doesn\'t clank about like all the other shields.  Stupid clanking shields.',
'good_icebarrel':'Don\'t limit yourself to a simple ice bucket.  You are better than that.',
'good_blacklumber':'Grows in graveyards',
'good_sweetbread':'Not actually bread.  And if it is indeed sweet, you picked a bad one.',
'good_porcelain':'An essential religious altar during those fuzzy college years.',
'good_ice':'A little bundle of chilled evil.  Don\'t let it escape.',
'good_finelumber':'Those with a friend who is into carpentry, should give this as a present',
'good_breadpudding':'Behold. Light cream drizzled over warm breadpudding.  Heaven awaits.',
'good_pottery':'A child, age 5, broke the last one.  Replica pottery ensures that his step-father will never find out.',
'good_stoutbarrel':'This barrel prefers the term \'stout\'  over diminutive titles like \'tiny\' or \'dwarven\'',
'good_blackwhiskey':'Duke Elba sold his soul to the Ice Witch for one stiff drink. This is what he quaffed.',
'good_ironrations':'The last warriors of the Flannish took these rations on their suicide mission to vanquish the spirit lords.  There are no more warrior flan.',
'good_prayerstones':'Yes, these prayer stones are made of foam, but it is certified blessed foam.',
'good_stewbarrel':'This is what happens when you cook a barrel of monkeys',
'good_deathpowder':'Produced by crushing dried mushrooms into powder.  A single pinch can aphyxiate a room.',
'good_heartymeals':'A meal for flan that require two seats when traveling coach.',
'good_flatbread':'The famous chef Rotoschooni made this dish for the Princess when he first cooked for her.  They eloped that night.',
'good_dullamulet':'An amulet for the flan that does not need to flaunt their immense wealth.',
'good_dullsceptre':'On the backside of this nondescript scepter is a spout that dispenses black whiskey.',
'good_dullcrown':'The dour workers of the stony west fear reflections so they scuff their metal and break all foreign mirrors.',
'good_potionofundeath':'Ha!  Juliet so wished she had this in that fine scene.',
'good_float':'Carry on.  Nothing to see here.',
'good_wineofdeath':'The distributor doesn\'t understand why this product sells so poorly.',
'good_wineofjoy':'Actual just standard wine, but the packaging sells it.',
'good_gunship':'Row, row, row your boat...BGOM!  Cannonball.',
'good_hairelixir':'You can put this on your tongue and pretend you have a beard.',
'good_glowingamulet':'The reverse of this pendant states \'In times of need, seek the glow of friends\'',
'good_glowingsceptre':'An inscription on the side of the scepter reads \'By working together, greatness is inevitable\'',
'good_glowingcrown':'Glowing words ring the band, spelling out \'Alone, you are nothing.\'',
'good_shadowamulet':'Minions sworn to the creeping ice wear such amulet to keep the heat of love at bay.',
'good_shadowsceptre':'The first of the ice lords created this vile device from an inky pool of bitterness.',
'good_shadowcrown':'If you ever stumble upon a shadow crown, burn it with fire.  The world hangs in balance.',
'good_icebust':'Mrs. Thatcher, is that you?',
'good_woodbust':'Even the teeth are wood. Wait! Those are my teeth!',
'good_chocolatebust':'Better than a bunny',
'good_porcelainbust':'When you grow older, you\'ll collect a full glass case of these.',
'good_chocolatestatue':'All good things are made of chocolate.',
'good_icestatue':'Amelia Plumson, an artist of great renown, died. Her last wish was to send a last message.  This melting statue was found on her daughter\'s doorstep.',
'good_porcelainstatue':'The nation came together to create this great work.  The pride you feel comes from the bonds you built.',
'good_woodstatue':'The sculptor of this carving was inspired by a time when he was lost in the subway.  A lady with ladybug boots gave him an apple and led him home.',
'good_mahnamahna':'Two twooo two two two',
'good_birthdaycake':'Another year, another cake, another tube of toothpaste.',
'good_magicbuns':'Magic Buns.  You just wanna squeeze \'em.',
'good_dullearrings':'Made of lead.  Proudly sold in America',
'good_glowingearrings':'There is a small switch in the back that makes these blink.  SOS!',
'good_shadowearrings':'If you wear your hair down, no one will see these.  Your little secret.  That and the location of the bloody ax.',
'good_earrings':'Rings for your ears.',
'good_glowingshield':'Friends shield us from loneliness like children shield politicians',
'good_absinthe':'No one knows the secret hallucinagenic ingredients of this madman\'s liquor.',
'good_manaorb':'Looks great on a lawn',
'good_stickybuns':'If children eat this treat with their fingers, they gain the magical ability to climb walls. While giggling maniacly.',
'good_pinkflamingo':'Looks so much better than a mana orb.  Dear neighbor, How about them apples?""',
'good_sundial':'Time, like a rampaging herd of wild stallions, leaves behind an amazing quantity of poop.',
'good_hammeroftime':'Stop. Hammered by time. Break me down.',
'good_sparkypants':'If you must one day put on some pants...make them sparky pants',
'good_dullarmor':'Hide from the world inside this tiny dull space.  No one can poke you now.',
'good_glowingarmor':'Every person who loves you (or your luxuriant hair) decreases your AC by 1.',
'good_shadowarmor':'This is the stuff that makes evil robots impervious to bullets.',
'good_bracelet':'Elegance is a small band that accents the sweet bones of the youthful wrist.',
'good_bangle':'A large rigid bracelet with Egyptian markings',
'good_armparty':'Past a certain age, it is wise to trade elegance for Hey, stop looking at my wrinkles.""',
'good_writofseduction':'A warrior of modern romance knows that the True Love sometimes needs a small kick forward.',
'good_glowingstatue':'My loved one died.  Please remember her.',
'good_crownedstatue':'The carved crown was so stunning that his people remembered him as a hero, not a drunk.',
'good_blackheart':'The shriveled heart of a flan that did not play nicely with others',
'good_junk':'Goods go in, junk comes out. Maybe you should use the recipedia!'}

# SHIM FOR DISPLAY NAMES
KEY_DISPLAY_NAMES = {
'good_food':'Food',
'good_wood':'Wood',
'good_water':'Water',
'good_stone':'Stone',
'good_barrel':'Barrel',
'good_oak':'Oak',
'good_bread':'Bread',
'good_bricks':'Bricks',
'good_spirits':'Spirits',
'good_lumber':'Lumber',
'good_perfume':'Perfume',
'good_gems':'Polished Gems',
'good_stew':'Stew',
'good_ore':'Ore',
'good_spices':'Spices',
'good_glass':'Glass',
'good_cookedfood':'Cooked Food',
'good_flour':'Flour',
'good_mana':'Mana',
'good_mulledwine':'Mulled Wine',
'good_shrines':'Shrines',
'good_potionofdeath':'Potion of Death',
'good_potionofjoy':'Potion of Joy',
'good_potionoflife':'Potion of Life',
'good_jewelry':'Jewelry',
'good_idols':'Idols',
'good_gunpowder':'Gunpowder',
'goodtype_crystal':'Crystal',
'good_onyx':'Onyx',
'good_jade':'Jade',
'good_opal':'Opal',
'good_amber':'Amber',
'good_silver':'Silver',
'good_diamond':'Diamond',
'good_sapphire':'Sapphire',
'good_ruby':'Ruby',
'good_amethyst':'Amethyst',
'good_rings':'Ring',
'good_necklace':'Necklace',
'good_shields':'Shield',
'good_hammers':'Hammers',
'good_largebarrel':'Large Barrel',
'good_blackoak':'Black Oak',
'good_blackbread':'Black Bread',
'good_firedbricks':'Fired Bricks',
'good_whiskey':'Whiskey',
'good_chair':'Chair',
'good_jewelrybox':'Jewelry Box',
'good_desk':'Desk',
'good_incense':'Incense',
'good_rockhammers':'Rock Hammers',
'good_beer':'Beer',
'good_fruitcake':'Fruit Cake',
'good_cinnamonrolls':'Cinnamon Rolls',
'good_catstatue':'Cat Statue',
'good_metalingot':'Metal Ingot',
'good_curry':'Curry',
'good_chowder':'Chowder',
'good_grog':'Grog',
'good_chili':'Chili',
'good_windows':'Windows',
'good_spyglass':'Spyglass',
'good_finebrandy':'Fine Brandy',
'good_crockpot':'Crockpot',
'good_lembascakes':'Lembas Cakes',
'good_luxuryfood':'Luxury Food',
'good_glue':'Glue',
'good_firebread':'Fire Bread',
'good_fineflour':'Fine Flour',
'good_sweetwine':'Sweet Wine',
'good_rowboat':'Rowboat',
'good_haircream':'Hair Cream',
'good_firering':'Fire Ring',
'good_poisonring':'Poison Ring',
'good_stonering':'Stone Ring',
'good_firenecklace':'Fire Necklace',
'good_poisonnecklace':'Poison Necklace',
'good_stonenecklace':'Stone Necklace',
'good_crystalshield':'Crystal Shield',
'good_spiritshield':'Spirit Shield',
'good_stealthshield':'Stealth Shield',
'good_icebarrel':'Ice Barrel',
'good_blacklumber':'Black Lumber',
'good_sweetbread':'Sweet Bread',
'good_porcelain':'Porcelain',
'good_ice':'Ice',
'good_finelumber':'Fine Lumber',
'good_breadpudding':'Bread Pudding',
'good_pottery':'Pottery',
'good_stoutbarrel':'Stout Barrel',
'good_blackwhiskey':'Black Whiskey',
'good_ironrations':'Iron Rations',
'good_prayerstones':'Prayer Stones',
'good_stewbarrel':'Stew Barrel',
'good_deathpowder':'Death Powder',
'good_heartymeals':'Hearty Meal',
'good_flatbread':'Flatbread',
'good_dullamulet':'Dull Amulet',
'good_dullsceptre':'Dull Sceptre',
'good_dullcrown':'Dull Crown',
'good_potionofundeath':'Potion of Undeath',
'good_float':'Ceremonial Float',
'good_wineofdeath':'Wine of Death',
'good_wineofjoy':'Wine of Joy',
'good_gunship':'Gunship',
'good_hairelixir':'Hair Elixir',
'good_glowingamulet':'Glowing Amulet',
'good_glowingsceptre':'Glowing Sceptre',
'good_glowingcrown':'Glowing Crown',
'good_shadowamulet':'Shadow Amulet',
'good_shadowsceptre':'Shadow Sceptre',
'good_shadowcrown':'Shadow Crown',
'good_icebust':'Ice Bust',
'good_woodbust':'Wood Bust',
'good_chocolatebust':'Chocolate Bust',
'good_porcelainbust':'Porcelain Bust',
'good_chocolatestatue':'Chocolate Statue',
'good_icestatue':'Ice Statue',
'good_porcelainstatue':'Porcelain Statue',
'good_woodstatue':'Wood Statue',
'good_mahnamahna':'Mahna Mahna',
'good_birthdaycake':'Birthday Cake',
'good_magicbuns':'Magic Buns',
'good_dullearrings':'Dull Earrings',
'good_glowingearrings':'Glowing Earrings',
'good_shadowearrings':'Shadow Earrings',
'good_earrings':'Earrings',
'good_glowingshield':'Glowing Shield',
'good_absinthe':'Absinthe',
'good_manaorb':'Mana Orb',
'good_stickybuns':'Sticky Buns',
'good_pinkflamingo':'Pink Flamingo',
'good_sundial':'Sundial',
'good_hammeroftime':'Hammer of Time',
'good_sparkypants':'Sparky Pants',
'good_dullarmor':'Dull Armor',
'good_glowingarmor':'Glowing Armor',
'good_shadowarmor':'Shadow Armor',
'good_bracelet':'Bracelet',
'good_bangle':'Statement Bangle',
'good_armparty':'Arm Party',
'good_writofseduction':'Writ of Seduction',
'good_glowingstatue':'Glowing Statue',
'good_crownedstatue':'Crowned Statue',
'good_blackheart':'Black Heart',
'good_junk':'Junk'}

if __name__ == '__main__':
    update_recipes()
