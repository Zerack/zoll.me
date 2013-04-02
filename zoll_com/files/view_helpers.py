'''
James D. Zoll

4/1/2013

Purpose: Defines helper functions for the primary views in the Files application.

License: This is a public work.

'''

# Local Imports
from files.models import Group_Member

def nav_group_entries(user):
    '''
    For a given user, returns a list of tuples of (group, group_url) for
    all groups that the user is a member of. This is for use in the navigation
    snippet.
    
    Keyword Arguments:
    user -> User Object. The currently authenticated user.
    
    '''
    
    if user.is_authenticated():    
        return [x.group.group for x in Group_Member.objects.filter(user=user).all()]
    return []