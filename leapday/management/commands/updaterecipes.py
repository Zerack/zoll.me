'''
James D. Zoll

6/28/2013

Purpose: Defines the updaterecipes command which will update recipe data when run as
         python manage.py updaterecipedata

Purpose: Defines the updatescarfdata command which will update scarf data when run as
         python manage.py updatescarfdata.
         
License: This is a public work.

'''

# Library Imports
from django.core.management.base import BaseCommand, CommandError

# Local Imports
from leapday.tasks.update_recipes import update_recipes

class Command(BaseCommand):
    args = ''
    help = 'Updates good and recipe information from sparkypants.com for the game Leap Day'

    def handle(self, *args, **options):
        update_recipes(out=self.stdout)