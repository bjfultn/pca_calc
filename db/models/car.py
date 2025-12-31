import django
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from logger import log
from pca_calc import settings
from pca_calc.class_table import class_table

class Car(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cars",
                             blank=True, null=True)
    year = models.CharField(max_length=4, null=True)
    make = models.CharField(max_length=30, null=True)
    model = models.CharField(max_length=30, null=True)
    color = models.CharField(max_length=30, null=True)
    weight = models.IntegerField(null=True,
        verbose_name="Enter your car's curb weight. Curb weight is the weight of the vehicle including a full tank of fuel and all standard equipment. It does not include the weight of the driver, any passengers, or cargo. If modified, it is preferred to measure the actual weight of your car with a full tank of fuel, and all modifications installed as ready to race. This can be accomplished at shops performing a corner balance alignment, you can Google 'public scales near me' to find DMV weigh stations, or you can email PCA LA requesting scales be brought to the next autocross. Be prepared to show photos proving your car's weight if it is significantly different than its original Curb Weight.\n\nCurb Weight:")
    horsepower = models.IntegerField(null=True,
        verbose_name="Enter your car's crank horsepower. This is the horsepower listed by the manufacturer (if your car is not modified). If your car is modified, assume 10% losses to convert wheel HP to crank HP as measured on a wheel dyno (preferred). If your car dyno'd at 386 whp (wheel horsepower) --> 386*1.10 = 424.6 crank hp --> enter 425. Note: Be prepared to show your dyno results if a fellow competitor asks.\n\nCrank Horsepower:")
    front_wheel_width = models.FloatField(null=True, verbose_name="To measure wheel width, find the measurement on the wheel's stamp (often XXJ, where XX is the width in inches).  This is the value wheel manufacturers advertise as the wheel width.  Alternatively, you can manually measure the distance between the two bead seats (the inner lips where the tire sits) with a tape measure or straight edge and a ruler. This 'bead seat to bead seat' measurement is the official rim width and will be roughly 1 inch less than the total outer width of the wheel.\n\nFront wheel width [in]:")
    rear_wheel_width = models.FloatField(null=True, verbose_name="Rear wheel width [in]")
    last_updated = models.DateTimeField(null=True, blank=True, auto_now=False, verbose_name="Last Updated")
    # picture = models.ImageField(upload_to="./avatars/", blank=True)

    def __str__(self):
        return "Vehicle: {} {} {} {}".format(self.color, self.year, self.make, self.model)

    def __repr__(self):
        return "<Car model: {} {} {} {}>".format(self.color, self.year, self.make, self.model)

    class Meta:
        ordering = ('-year',)

    def class_name(self):
        class_string = ''
        try:
            if self.total_points():
                for cls,rng in class_table.items():
                    if rng[0] < self.total_points() <= rng[1]:
                        class_string = cls
            if self.tires.last().race_tires:
                class_string = f'CCR ({class_string})'
            return class_string
        except Exception as e:
            return e

    def base_points(self):
        wheels = 5*(self.front_wheel_width + self.rear_wheel_width - 12)
        if wheels < 0:
            wheels = 0
        bp = (4000 / (self.weight/self.horsepower)) + (int(self.year) - 2010) + \
             wheels

        return bp

    def total_points(self):
        try:
            if self.tires.count() and self.upgrades.count():
                tp = self.base_points()
                tp += self.tires.last().tire_points()
                tp += self.upgrades.last().upgrade_points()
            else:
                tp = 0
        except:
            tp = 0

        return tp
        

class CarCreateForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['user', 'last_updated']
    
    def clean_weight(self):
        content = self.cleaned_data['weight']
        if content > 0:
            return content
        else:
            raise ValidationError("weight must be greater than zero")

    def clean_horsepower(self):
        content = self.cleaned_data['horsepower']
        if content > 0:
            return content
        else:
            raise ValidationError("horsepower must be greater than zero")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            # Convert newlines in labels to <br> tags for proper rendering
            if self.fields[field].label and '\n' in self.fields[field].label:
                self.fields[field].label = mark_safe(
                    self.fields[field].label.replace('\n', '<br>')
                )

