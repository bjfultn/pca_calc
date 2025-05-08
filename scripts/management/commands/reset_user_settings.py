from django.core.management.base import BaseCommand, CommandError
from users.models import User

class Command(BaseCommand):

    help = 'Reset all persistent user data settings related to star and candidate tables'

    def handle(self, *args, **options):
        ## This class remains here as an example of a script that can be from from the commandline in the django framework as:
        ## python manage.py script_name
        users = User.objects.all()
        for user in users:
            print("-------------")
            print(user.name())
            print("Current Settings")
            print(user.data)
            print("Cleared Settings")
            user.data = {}
            user.save(update_fields=['data'])
            print(user.data)
