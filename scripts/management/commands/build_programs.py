from django.core.management.base import BaseCommand, CommandError
from db.models import *

class Command(BaseCommand):

    help = 'Program ingestion and star assignements'

    def handle(self, *args, **options):
        ## This class remains here as an example of a script that can be from from the commandline in the django framework as: 
        ## python manage.py script_name
        print("Program ingestion is handled through jump-rake ingest programs")
