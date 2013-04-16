'''
James D. Zoll

4/1/2013

Purpose: Defines the updatescarfdata command which will update scarf data when run as
         python manage.py updatescarfdata.
         
License: This is a public work.

'''

# Library Imports
from django.core.management.base import BaseCommand, CommandError

# Local Imports
from scarf.tasks.update_temps import update_temps

class Command(BaseCommand):
    args = ''
    help = 'Updates temperature data for My Year In Temperatures'

    def handle(self, *args, **options):
        update_temps(out=self.stdout)