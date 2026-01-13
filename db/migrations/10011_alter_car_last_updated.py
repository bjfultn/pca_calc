# Generated manually to fix last_updated field

from django.db import migrations, models
from django.utils import timezone


def nullify_last_updated(apps, schema_editor):
    """Set all existing last_updated values to NULL."""
    Car = apps.get_model('db', 'Car')
    Car.objects.all().update(last_updated=None)


def reverse_nullify_last_updated(apps, schema_editor):
    """Reverse migration - set last_updated to current time for all cars."""
    Car = apps.get_model('db', 'Car')
    Car.objects.all().update(last_updated=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('db', '10010_auto_20251230_1728'),
    ]

    operations = [
        # First, nullify all existing values
        migrations.RunPython(nullify_last_updated, reverse_nullify_last_updated),
        # Then, alter the field to remove auto_now
        migrations.AlterField(
            model_name='car',
            name='last_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Updated'),
        ),
    ]

