# Generated by Django 2.2.24 on 2021-12-27 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0023_auto_20211227_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='horsepower',
            field=models.IntegerField(null=True, verbose_name='Factory rating or measured at the crank. \\\n                                Assume 10% losses to convert wheel HP to crank HP.'),
        ),
        migrations.AlterField(
            model_name='car',
            name='weight',
            field=models.IntegerField(null=True, verbose_name='Curb weight or measured weight if known [lb]'),
        ),
        migrations.AlterField(
            model_name='tire',
            name='dot',
            field=models.BooleanField(default=True, verbose_name='Are the tires DOT rated?'),
        ),
        migrations.AlterField(
            model_name='tire',
            name='front_section_width',
            field=models.IntegerField(null=True, verbose_name='Section width of front tires [mm]'),
        ),
        migrations.AlterField(
            model_name='tire',
            name='rear_section_width',
            field=models.IntegerField(null=True, verbose_name='Section width of rear tires [mm]'),
        ),
        migrations.AlterField(
            model_name='tire',
            name='treadwear',
            field=models.IntegerField(null=True, verbose_name='Treadwear rating'),
        ),
    ]
