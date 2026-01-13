from django.db import migrations

UPGRADE_FIELDS = [
    'mid_engine', 'traction_control', 'induction', 'engine_head', 'camshaft',
    'forced_induction', 'boost', 'displacement', 'muffler', 'cats', 'headers',
    'differential', 'final_drive', 'pdk', 'shocks', 'shock_tower',
    'factory_springs', 'aftermarket_springs', 'fixed_sway', 'adj_sway',
    'custom_suspension', 'camber', 'spherical_bearings', 'tube_frame',
    'factory_aero', 'oem_aero', 'aftermarket_aero', 'windshield_delete', 'brakes'
]

def migrate_upgrades_to_jsonfield(apps, schema_editor):
    Upgrades = apps.get_model('db', 'Upgrades')
    for upgrade in Upgrades.objects.all():
        values = {}
        for field in UPGRADE_FIELDS:
            values[field] = getattr(upgrade, field, None)
        upgrade.values = values
        upgrade.save(update_fields=['values'])

class Migration(migrations.Migration):
    dependencies = [
        ('db', '10000_auto_20251102_2221'),
    ]
    operations = [
        migrations.RunPython(migrate_upgrades_to_jsonfield, reverse_code=migrations.RunPython.noop),
    ]
