import django
from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from logger import log
from pca_calc import settings

class Tire(models.Model):
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name="tires",
                             blank=True, null=True)
    front_section_width = models.IntegerField(null=True,
                            verbose_name="Section width of front tires [mm]")
    rear_section_width = models.IntegerField(null=True,
                            verbose_name="Section width of rear tires [mm]")
    treadwear = models.IntegerField(null=True,
                            verbose_name="Treadwear rating")
    dot = models.BooleanField(default=True,
                            verbose_name="Are the tires DOT rated?")

    class Meta:
        ordering = ('-rear_section_width',)

    def __str__(self):
        return "Tires: {} front, {} rear".format(self.front_section_width,
                                                 self.rear_section_width)

    def __repr__(self):
        return "<Tire model: {} {} {} {}>".format(self.color, self.year, self.make, self.model)

    def tire_points(self):
        try:
            tp = (self.front_section_width - 205) + (self.rear_section_width - 205)

            if not self.dot:
                tp += 140
            elif 140 <= self.treadwear <= 200:
                tp += 20
            elif 50 <= self.treadwear < 139:
                tp += 40
            elif 1 <= self.treadwear < 49:
                tp += 40
            elif self.treadwear == 0:
                tp += 120
        except TypeError:
            tp = 0

        return tp
    

class TireCreateForm(forms.ModelForm):
    class Meta:
        model = Tire
        exclude = ['car']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'