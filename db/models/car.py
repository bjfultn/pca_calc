import django
from django import forms
from django.db import models
from django.core.exceptions import ValidationError

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
                                verbose_name="Curb weight or measured weight [lb]")
    horsepower = models.IntegerField(null=True,
                                verbose_name=r"Factory rated HP or measured at the crank. Assume 10% losses to convert wheel HP to crank HP.")
    front_wheel_width = models.FloatField(null=True, verbose_name="Front wheel width [in]")
    rear_wheel_width = models.FloatField(null=True, verbose_name="Rear wheel width [in]")
    # picture = models.ImageField(upload_to="./avatars/", blank=True)

    def __str__(self):
        return "Vehicle: {} {} {} {}".format(self.color, self.year, self.make, self.model)

    def __repr__(self):
        return "<Car model: {} {} {} {}>".format(self.color, self.year, self.make, self.model)

    class Meta:
        ordering = ('-year',)

    def class_name(self):
        try:
            if self.total_points():
                for cls,rng in class_table.items():
                    if rng[0] < self.total_points() <= rng[1]:
                        return cls
        except:
            return ''

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
        exclude = ['user']
    
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

