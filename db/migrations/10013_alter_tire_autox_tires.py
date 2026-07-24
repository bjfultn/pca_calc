from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '10012_alter_car_horsepower'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tire',
            name='autox_tires',
            field=models.BooleanField(default=False, verbose_name='Do you have autox tires? Treadwear greater than or equal to 140, but less than or equal to 200 (+20 points). Note that the AutoX committee has voted, and the Vitour Sonic 200tw tire will not be allowed as an "AutoX tire." They are considered a "Race tire" and will compete in CCR.'),
        ),
    ]
