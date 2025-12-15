import json
from django.core.management.base import BaseCommand
from django.db import connection
from db.models import Upgrades

# List of all old upgrade fields to export
UPGRADE_FIELDS = [
    'mid_engine', 'traction_control', 'induction', 'engine_head',
    'camshaft', 'forced_induction', 'boost', 'displacement', 'muffler',
    'cats', 'headers', 'differential', 'final_drive', 'pdk', 'shocks',
    'shock_tower', 'factory_springs', 'aftermarket_springs',
    'fixed_sway', 'adj_sway', 'custom_suspension', 'camber',
    'spherical_bearings', 'tube_frame', 'factory_aero', 'oem_aero',
    'aftermarket_aero', 'windshield_delete', 'brakes'
]


class Command(BaseCommand):
    help = 'Export all car upgrades to upgrades_backup.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--old-schema',
            action='store_true',
            help='Export from old database schema with individual columns',
        )

    def handle(self, *args, **options):
        data = []
        use_old_schema = options.get('old_schema', False)

        # Check if we're using the old schema (individual columns)
        # or new schema (JSONField)
        with connection.cursor() as cursor:
            query = """
                SELECT column_name FROM information_schema.columns
                WHERE table_name='db_upgrades'
            """
            cursor.execute(query)
            columns = [row[0] for row in cursor.fetchall()]
            has_individual_columns = 'mid_engine' in columns

        if use_old_schema or has_individual_columns:
            # Old schema: read from individual database columns
            self.stdout.write(
                'Exporting from OLD schema (individual columns)...'
            )
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
                        }
                    }
                    data.append(record)
        else:
            # New schema: read from JSONField 'values'
            self.stdout.write('Exporting from NEW schema (JSONField)...')
            for upgrade in Upgrades.objects.all():
                values_dict = upgrade.values if upgrade.values else {}
                record = {
                    'id': upgrade.id,
                    'car_id': upgrade.car_id,
                    'fields': {
                        field: values_dict.get(field, None)
                        for field in UPGRADE_FIELDS
                    }
                }
                data.append(record)

        output_file = 'upgrades_backup.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        msg = f'Exported {len(data)} upgrades to {output_file}'
        self.stdout.write(self.style.SUCCESS(msg))
