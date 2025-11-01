
import math
import django
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from logger import log
from pca_calc import settings

# Default hard-coded points (used as fallback if DB definitions aren't available)
DEFAULT_UPGRADE_POINTS = {
    'mid_engine': 15,
    'traction_control': 10,
    'induction': 40,
    'engine_head': 50,
    'camshaft': 50,
    'forced_induction': 150,
    'boost': 100,
    # displacement handled specially (per-unit multiplier fallback)
    'muffler': 5,
    'cats': 5,
    'headers': 5,
    'differential': 20,
    'final_drive': 40,
    'pdk': 15,
    'shocks': 20,
    'shock_tower': 10,
    'factory_springs': 15,
    'aftermarket_springs': 30,
    'fixed_sway': 10,
    'adj_sway': 20,
    'custom_suspension': 10,
    'camber': 20,
    'spherical_bearings': 10,
    'tube_frame': 100,
    'factory_aero': 10,
    'oem_aero': 20,
    'aftermarket_aero': 40,
    'windshield_delete': 60,
    'brakes': 20,
}


class UpgradeDefinition(models.Model):
        """Editable definitions for each upgrade type.

        key: matches the field name on `Upgrades` (e.g. 'mid_engine').
        points: fixed points to apply when the boolean is True.
        per_unit: if set, used for numeric fields like `displacement` as
            `ceil(per_unit * value)`.
        """
        key = models.CharField(max_length=64, unique=True)
        label = models.CharField(max_length=200)
        description = models.TextField(blank=True)
        points = models.FloatField(default=0)
        per_unit = models.FloatField(null=True, blank=True)
        order = models.IntegerField(default=0)

        class Meta:
                ordering = ['order', 'key']

        def __str__(self):
                return f"{self.label} ({self.key})"

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

        # Try to load editable definitions from DB; fall back to field.verbose_name
        try:
            defs = {d.key: d for d in UpgradeDefinition.objects.all()}
        except Exception:
            defs = {}

        for field in self._meta.get_fields():
            # skip relationship/id fields
            if not hasattr(self, field.name):
                continue

            label = None
            if field.name in defs:
                label = defs[field.name].description or defs[field.name].label
            else:
                label = getattr(field, 'verbose_name', field.name)

            val = getattr(self, field.name)
            # displacement is numeric; show its label and value
            if field.name == 'displacement':
                not_installed += f"{label}: {val}%<br>"
                continue

            if val is True:
                installed += f"{label}<br>"
            elif val is False:
                not_installed += f"{label}<br>"

        output = installed + "<br>" + not_installed
        return mark_safe(output)

    def upgrade_points(self):
        # Try to load editable definitions from DB; fall back to hard-coded values
        try:
            defs = {d.key: d for d in UpgradeDefinition.objects.all()}
        except Exception:
            defs = {}

        tp = 0

        # Helper to get points for a boolean field
        def points_for(key, value):
            if key in defs:
                try:
                    return int(defs[key].points) * int(bool(value))
                except Exception:
                    return int(DEFAULT_UPGRADE_POINTS.get(key, 0)) * int(bool(value))
            return int(DEFAULT_UPGRADE_POINTS.get(key, 0)) * int(bool(value))

        # Sum up boolean-based upgrades
        for key in DEFAULT_UPGRADE_POINTS.keys():
            # displacement handled separately
            if key == 'displacement':
                continue
            tp += points_for(key, getattr(self, key, False))

        # Forced special-case: displacement
        if 'displacement' in defs and defs['displacement'].per_unit:
            try:
                tp += math.ceil(defs['displacement'].per_unit * self.displacement)
            except Exception:
                tp += math.ceil(3.6 * self.displacement)
        else:
            tp += math.ceil(3.6 * self.displacement)

        return tp
    

class UpgradesCreateForm(forms.ModelForm):
    class Meta:
        model = Upgrades
        exclude = ['car']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'