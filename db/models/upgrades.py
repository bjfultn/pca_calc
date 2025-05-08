
import math
import django
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from logger import log
from pca_calc import settings

class Upgrades(models.Model):
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name="upgrades",
                             blank=True, null=True)
    mid_engine = models.BooleanField(default=False,
        verbose_name="Is your car mid-engine or all electric? (15 points)")
    traction_control = models.BooleanField(default=False,
        verbose_name="Electronically adjustable shocks and/or active suspension, including PASM (10 points)")
    induction = models.BooleanField(default=False,
        verbose_name="Induction system modifications (e.g. upgrade carbs to fuel injection) (40 points)")
    engine_head = models.BooleanField(default=False,
        verbose_name="Non-stock heads (e.g. port/polish, compression changes) (50 points)")
    camshaft = models.BooleanField(default=False,
        verbose_name="Non-stock camshaft (50 points)")
    forced_induction = models.BooleanField(default=False,
        verbose_name="Added a turbo or supercharger? (150 points)")
    boost = models.BooleanField(default=False,
        verbose_name="Increased or adjustable boost, or modifications to the wastegate or turbocharger (100 points)")
    displacement = models.IntegerField(default=0,
        verbose_name="Is the engine displacement larger than stock? If yes, by what percentage? (0=no increase, 100=doubled displacement) (36 x fractional increase points")
    muffler = models.BooleanField(default=False,
        verbose_name="Upgraded or deleted muffler (5 points)")
    cats = models.BooleanField(default=False,
        verbose_name="Deleted catalytic converter (5 points)")
    headers = models.BooleanField(default=False,
        verbose_name="Non-stock exhaust manifold or headers (5 points)")
    differential = models.BooleanField(default=False,
        verbose_name="Does your car have a stock/aftermarket LSD or AWD? (20 points)")
    final_drive = models.BooleanField(default=False,
        verbose_name="Non-stock final drive ratio (40 points)")
    pdk = models.BooleanField(default=False,
        verbose_name="Is your car an EV or does your car have a PDK, dual clutch, or sequential transmission? (15 points)")
    shocks = models.BooleanField(default=False,
        verbose_name="Non-stock shocks with external reservoirs or 2+ way adjustability (20 points)")
    shock_tower = models.BooleanField(default=False,
        verbose_name="Non-stock shock tower brace (10 point)")
    factory_springs = models.BooleanField(default=False,
        verbose_name="Non-stock factory springs (within the same series) (15  points)")
    aftermarket_springs = models.BooleanField(default=False,
        verbose_name="Aftermarket springs or factory springs from a different model series. (30 points)")
    fixed_sway = models.BooleanField(default=False,
        verbose_name="Non-stock non-adjustable sway bar(s) (10 points)")
    adj_sway = models.BooleanField(default=False,
        verbose_name="Non-stock adjustable sway bar(s) (20 points)")
    custom_suspension = models.BooleanField(default=False,
        verbose_name="Suspension changes to lower a car that require machining, welding, etc. or their equivalent. (10 points)")
    camber = models.BooleanField(default=False,
        verbose_name="Any change to the suspension components or mounting points to increase available negative camber (20 points)")
    spherical_bearings = models.BooleanField(default=False,
        verbose_name="Installation of “Monoball” suspension bushings or equivalent 10 (points)")
    tube_frame = models.BooleanField(default=False,
        verbose_name="Tube frame chassis (100 points)")
    factory_aero = models.BooleanField(default=False,
        verbose_name="Non-stock aero devices that came from another car within the same model series. (10 points)")
    oem_aero = models.BooleanField(default=False,
        verbose_name="Non-stock aero devices that came from another car not within the same model series. (20 points)")
    aftermarket_aero = models.BooleanField(default=False,
        verbose_name="Any aftermarket aero devices. (40 points)")
    windshield_delete = models.BooleanField(default=False,
        verbose_name="Removal or alteration of windshield (other than replacement with lighter weight materials) (60 points)")
    brakes = models.BooleanField(default=False,
        verbose_name="Brake Upgrades (other than drilled/gas slotted stock rotors, brake pads, master cylinder, or aftermarket rotors with no increase in diameter). Includes factory or post-delivery installation of ceramic brakes (20 points)")

    def __str__(self):
        return "Upgrade points: {}".format(self.upgrade_points())

    def __repr__(self):
        return "<Upgrades model>"

    def upgrade_table(self):
        installed = "<h5>Installed:</h5>"
        not_installed = "<h5>Not installed:</h5>"
        for field in self._meta.get_fields():
            if getattr(self, field.name) == True:
                installed += field.verbose_name + "<br>"
            elif getattr(self, field.name) == False:
                not_installed += field.verbose_name + "<br>"

        output = installed + "<br>" + not_installed
        return mark_safe(output)

    def upgrade_points(self):
        tp = 15*self.mid_engine
        tp += 10*self.traction_control
        tp += 40*self.induction
        tp += 50*self.engine_head
        tp += 50*self.camshaft
        tp += 150*self.forced_induction
        tp += 100*self.boost
        tp += math.ceil(3.6*self.displacement)
        tp += 5*self.muffler
        tp += 5*self.cats
        tp += 5*self.headers
        tp += 20*self.differential
        tp += 40*self.final_drive
        tp += 15*self.pdk
        tp += 20*self.shocks
        tp += 10*self.shock_tower
        tp += 15*self.factory_springs
        tp += 30*self.aftermarket_springs
        tp += 10*self.fixed_sway
        tp += 20*self.adj_sway
        tp += 10*self.custom_suspension
        tp += 20*self.camber
        tp += 10*self.spherical_bearings
        tp += 100*self.tube_frame
        tp += 10*self.factory_aero
        tp += 20*self.oem_aero
        tp += 40*self.aftermarket_aero
        tp += 60*self.windshield_delete
        tp += 20*self.brakes

        return tp
    

class UpgradesCreateForm(forms.ModelForm):
    class Meta:
        model = Upgrades
        exclude = ['car']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'