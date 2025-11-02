import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction

try:
    from db.models.upgrades import UpgradeDefinition
except Exception:
    UpgradeDefinition = None


class Command(BaseCommand):
    help = 'Populate UpgradeDefinition rows from preserved definitions JSON'

    def handle(self, *args, **options):
        if UpgradeDefinition is None:
            self.stderr.write(
                'Could not import UpgradeDefinition. Are migrations applied?'
            )
            return

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'upgrade_definitions.json'
        )

        if not os.path.exists(json_path):
            self.stderr.write(
                f'Definitions file not found at {json_path}. '
                'Run preserve_upgrade_defs first!'
            )
            return

        try:
            with open(json_path) as f:
                definitions = json.load(f)
        except Exception as e:
            self.stderr.write(f'Failed to load definitions: {e}')
            return

        created = 0
        updated = 0

        with transaction.atomic():
            for defn in definitions:
                obj, created_flag = UpgradeDefinition.objects.update_or_create(
                    key=defn['key'],
                    defaults={
                        'label': defn['label'],
                        'description': defn['description'],
                        'points': defn['points'],
                        'per_unit': defn['per_unit'],
                        'order': defn['order']
                    }
                )

                if created_flag:
                    created += 1
                    self.stdout.write(f'Created UpgradeDefinition for "{defn["key"]}"')
                else:
                    updated += 1
                    self.stdout.write(f'Updated UpgradeDefinition for "{defn["key"]}"')

        self.stdout.write(
            self.style.SUCCESS(f'Done. Created: {created}, Updated: {updated}')
        )
