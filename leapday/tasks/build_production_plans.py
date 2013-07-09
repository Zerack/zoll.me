''' 
James D. Zoll

7/2/2013

Purpose: Functionality to update the Production_Plan and associated tables,
         to enable users to determine the most valuable crafting available
         to them.

License: This is a public work.

'''

# System Imports
import itertools

# Library Imports
from django.db import connection

# Local Imports
from leapday.models import Good, Production_Plan, Production_Plan_Entry 
from leapday.models import Production_Plan_Entry_Goods, Base_Material

# Constants and Configuration
NUM_RESULTS = 10
MAX_BASE_QUANTITY = 10

# Since Django won't follow Foreign Keys this direction, we have to shim it ourselves.
VALID_GOODS = Good.objects.all().exclude(good_type='goodtype_crystal')
obj_dict = dict([(obj.id, obj) for obj in VALID_GOODS])

base_ingredients = Base_Material.objects.select_related('ingredient').filter(product__in=VALID_GOODS).all()
base_relation_dict = {}
for b in base_ingredients:
    base_relation_dict.setdefault(b.product_id, []).append(b)
for b_id, related_items in base_relation_dict.items():
    obj_dict[b_id].shim_base_ingredients = related_items
    
for cur_good in VALID_GOODS:
    for base_ingredient in cur_good.shim_base_ingredients:
        setattr(cur_good, base_ingredient.ingredient.key.split('_')[-1], base_ingredient.quantity)
        
VALID_GOODS = filter(lambda x: (x.water <= MAX_BASE_QUANTITY and
                                x.food <= MAX_BASE_QUANTITY and
                                x.wood <= MAX_BASE_QUANTITY and
                                x.stone <= MAX_BASE_QUANTITY and
                                x.crystal <= MAX_BASE_QUANTITY), VALID_GOODS)

def build_production_plans():
    '''
    Clears the current database of production plans, and then uses the existing
    data in the Goods table to build up a new set up production plans
    for all combinations of base goods up to MAX_BASE_QUANTITY
    
    '''
    
    # Executing calc_best_worker will populate the memo, which will will
    # then use to push data into the database.
    memo = {}
    calc_best_worker(*([MAX_BASE_QUANTITY for _ in xrange(5)] + [memo]))
    return memo

cct = 0
def calc_best_worker(r, f, w, s, c, memo):
    if r == f == w == s == c == 0:
        return [(0,[])]
    
    if (r,f,w,s,c) in memo:
        return memo[(r,f,w,s,c)]
    
    results = []
    global cct
    cct += 1
    for cur_good in VALID_GOODS:
        # If we have insufficient resources to craft this item, skip.
        if (cur_good.water > r or
            cur_good.food > f or
            cur_good.wood > w or
            cur_good.stone > s or
            cur_good.crystal > c):
            continue
        
        t = calc_best_worker(r-cur_good.water, f-cur_good.food, w-cur_good.wood, s-cur_good.stone, c-cur_good.crystal ,memo)
        results = keep_needed(results, map(lambda x: (x[0] + cur_good.value, x[1] + [cur_good]), t))
        
    memo[(r,f,w,s,c)] = results
    return results

knt = 0
def keep_needed(a, b):    
    '''
    a and b are guaranteed to be sorted in order of
    most valuable to least valuable. Within equal value,
    sets with fewer unique items are first.
    
    '''
    
    global knt
    
    start = time.time()
    
    memo = {}
    result = []
    
    a_i = 0
    b_i = 0
    
    while a_i < len(a) and b_i < len(b) and len(result) < NUM_RESULTS:
        a_k = tuple(sorted(a[a_i][1], key=lambda x: x.key))
        b_k = tuple(sorted(b[b_i][1], key=lambda x: x.key))
                
        if a[a_i][0] > b[b_i][0]:
            if a_k not in memo:
                memo[a_k] = True
                result.append(a[a_i])
            a_i += 1
        elif a[a_i][0] < b[b_i][0]:
            if b_k not in memo:
                memo[b_k] = True
                result.append(b[b_i])
            b_i += 1
        else:
            a_s = set(a[a_i][1])
            b_s = set(b[b_i][1])
            if len(a_s) < len(b_s):
                if a_k not in memo:
                    memo[a_k] = True
                    result.append(a[a_i])
                a_i += 1
            else:
                if b_k not in memo:
                    memo[b_k] = True
                    result.append(b[b_i])
                b_i += 1
                
    if len(result) == NUM_RESULTS:
        return result
    elif a_i == len(a):
        while b_i < len(b) and len(result) < NUM_RESULTS:
            b_k = tuple(sorted(b[b_i][1], key=lambda x: x.key))
            if b_k not in memo:
                memo[b_k] = True
                result.append(b[b_i])
            b_i += 1
    else:
        while a_i < len(a) and len(result) < NUM_RESULTS:
            a_k = tuple(sorted(a[a_i][1], key=lambda x: x.key))
            if a_k not in memo:
                memo[a_k] = True
                result.append(a[a_i])
            a_i += 1
    
    knt += time.time() - start    
    return result

if __name__ == '__main__':
    import time
    
    a = time.time()
    r = build_production_plans()
    b = time.time()
    
    print 'Total execution time: {0}'.format(b - a)
    print 'Generated {0} entries.'.format((MAX_BASE_QUANTITY+1)**5)
    print 'Each entry has {0} possibilities.'.format(NUM_RESULTS)
    print '\nTime in list manipulation: {0}'.format(knt)
    print 'Iterations of all goods loop: {0}'.format(cct)
    
    #for k, v in r.iteritems():
    #    print '{0}: {1}'.format(repr(k), repr(v))
    print r[(10,10,10,10,10)]
