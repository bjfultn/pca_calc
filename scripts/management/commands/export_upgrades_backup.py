import json
from django.core.management.base import BaseCommand
from db.models import Upgrades

# List of all old upgrade fields to export
UPGRADE_FIELDS = [
    'mid_engine', 'traction_control', 'induction', 'engine_head', 'camshaft',
    'forced_induction', 'boost', 'displacement', 'muffler', 'cats', 'headers',
    'differential', 'final_drive', 'pdk', 'shocks', 'shock_tower',
    'factory_springs', 'aftermarket_springs', 'fixed_sway', 'adj_sway',
    'custom_suspension', 'camber', 'spherical_bearings', 'tube_frame',
    'factory_aero', 'oem_aero', 'aftermarket_aero', 'windshield_delete', 'brakes'
]

class Command(BaseCommand):
    help = 'Export all car upgrades to upgrades_backup.json'

    def handle(self, *args, **options):
        data = []
        for upgrade in Upgrades.objects.all():
            record = {
                'id': upgrade.id,
                'car_id': upgrade.car_id,
                'fields': {field: getattr(upgrade, field, None) for field in UPGRADE_FIELDS}
            }
            data.append(record)
        with open('upgrades_backup.json', 'w') as f:
            json.dump(data, f, indent=2)
        self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} upgrades to upgrades_backup.json'))
