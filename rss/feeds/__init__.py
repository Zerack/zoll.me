'''
James D. Zoll

4/2/2013

Purpose: Aggregates all active feeds into one dictionary, with
         keys being teh feed short name.

License: This is a public work.

'''

import ch, egs, scarf

# Prepare a dictionary of feeds for use by view functions.
feeds = {}
for mod in [ch, egs, scarf]:
    feeds[mod.feed.name] = mod.feed