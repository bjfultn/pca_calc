# Generated by Django 2.2.24 on 2021-12-22 01:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0015_auto_20211221_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('front_section_width', models.IntegerField(default=225)),
                ('rear_section_width', models.IntegerField(default=255)),
                ('treadwear', models.IntegerField(default=200)),
                ('dot', models.BooleanField(default=True)),
                ('car', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tires', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
