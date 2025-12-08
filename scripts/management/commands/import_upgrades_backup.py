import json
from django.core.management.base import BaseCommand
from db.models.upgrades import Upgrades

class Command(BaseCommand):
    help = 'Import upgrades from a backup JSON file into the Upgrades table.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the upgrades backup JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        with open(json_file, 'r') as f:
            upgrades_data = json.load(f)

        created = 0
        updated = 0
        for item in upgrades_data:
            car_id = item.get('car_id')
            values = item.get('fields', {})
            if not car_id:
                self.stdout.write(self.style.WARNING(f'Skipping item with no car_id: {item}'))
                continue
            obj, was_created = Upgrades.objects.update_or_create(
                car_id=car_id,
                defaults={'values': values}
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Import complete: {created} created, {updated} updated.'))
