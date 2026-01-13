import json
from django.core.management.base import BaseCommand
from django.db import connection

# List of all old upgrade fields to export
UPGRADE_FIELDS = [
    'mid_engine', 'traction_control', 'induction', 'engine_head',
    'camshaft', 'forced_induction', 'boost', 'displacement', 'muffler',
    'cats', 'headers', 'differential', 'final_drive', 'pdk', 'shocks',
    'shock_tower', 'factory_springs', 'aftermarket_springs',
    'fixed_sway', 'adj_sway', 'custom_suspension', 'camber',
    'spherical_bearings', 'tube_frame', 'factory_aero', 'oem_aero',
    'aftermarket_aero', 'windshield_delete', 'brakes',
]


class Command(BaseCommand):
    help = 'Export all car upgrades from old schema to upgrades_backup.json'

    def handle(self, *args, **options):
        data = []

        with connection.cursor() as cursor:
            field_list = ', '.join(UPGRADE_FIELDS)
            query = f"SELECT id, car_id, {field_list} FROM db_upgrades"
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]

            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                record = {
                    'id': row_dict['id'],
                    'car_id': row_dict['car_id'],
                    'fields': {
                        field: row_dict.get(field)
                        for field in UPGRADE_FIELDS
                    },
                }
                data.append(record)

        output_file = 'upgrades_backup.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        msg = f'Exported {len(data)} upgrades to {output_file}'
        self.stdout.write(self.style.SUCCESS(msg))