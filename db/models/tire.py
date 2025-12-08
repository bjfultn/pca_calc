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
    race_tires = models.BooleanField(default=False,
                            verbose_name="Do you have race tires? Treadwear less than 140, or no official treadwear will automatically put your car into CC18 as the penalty is applied during registration. Be sure to check the box during registration.")
    autox_tires = models.BooleanField(default=False,
                            verbose_name="Do you have autox tires? Treadwear greater than or equal to 140, but less than or equal to 200 (+20 points)")
    street_tires = models.BooleanField(default=False,
                            verbose_name="Do you have street tires? Treadwear greater than 200 (+0 points)")

    class Meta:
        ordering = ('-rear_section_width',)

    def __str__(self):
        return "Tires: {}mm front, {}mm rear".format(self.front_section_width,
                                                 self.rear_section_width)

    def __repr__(self):
        if self.race_tires:
            return "<Tire model: {}/{}mm Race Tires>".format(self.front_section_width, self.rear_section_width)
        elif self.autox_tires:
            return "<Tire model: {}/{}mm Autox Tires>".format(self.front_section_width, self.rear_section_width)
        elif self.street_tires:
            return "<Tire model: {}/{}mm Street Tires>".format(self.front_section_width, self.rear_section_width)
        else:
            return "<Tire model: {}/{}mm>".format(self.front_section_width, self.rear_section_width)

    def tire_points(self):
        try:
            tp = (self.front_section_width - 205) + (self.rear_section_width - 205)

            if self.autox_tires:
                tp += 20
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

    def clean(self):
        cleaned_data = super().clean()
        tire_flags = [
            cleaned_data.get('race_tires'),
            cleaned_data.get('autox_tires'),
            cleaned_data.get('street_tires'),
        ]

        if sum(bool(flag) for flag in tire_flags) != 1:
            raise ValidationError("Select exactly one tire type option.")

        return cleaned_data