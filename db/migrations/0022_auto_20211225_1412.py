# Generated by Django 2.2.24 on 2021-12-25 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0021_auto_20211222_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='upgrades',
            name='aftermarket_springs',
            field=models.BooleanField(default=False, verbose_name='Aftermarket springs or factory springs from a different model series.'),
        ),
        migrations.AddField(
            model_name='upgrades',
            name='factory_springs',
            field=models.BooleanField(default=False, verbose_name='Non-stock factory springs (within the same series)'),
        ),
        migrations.AddField(
            model_name='upgrades',
            name='mid_engine',
            field=models.BooleanField(default=False, verbose_name='Does your car have a mid-engine layout?'),
        ),
        migrations.AddField(
            model_name='upgrades',
            name='traction_control',
            field=models.BooleanField(default=False, verbose_name='Stock or non-stock traction and/or yaw control (e.g. PASM)'),
        ),
    ]
