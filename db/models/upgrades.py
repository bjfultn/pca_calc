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
    values = models.JSONField(default=dict, help_text="Stores upgrade values as {key: value}")

    class Meta:
        verbose_name = "Car Upgrades"
        verbose_name_plural = "Car Upgrades"


    def __getattr__(self, name):
        """Support getting upgrade values as if they were fields (car.upgrades.mid_engine)"""
        upgrade_defs = object.__getattribute__(self, '_upgrade_defs')
        if name in upgrade_defs:
            return self.values.get(name, False if upgrade_defs[name].per_unit is None else 0)
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        """Support setting upgrade values as if they were fields (car.upgrades.mid_engine = True)"""
        if name != '_upgrade_defs':
            upgrade_defs = object.__getattribute__(self, '_upgrade_defs')
            if name in upgrade_defs:
                if self.values is None:
                    self.values = {}
                self.values[name] = value
                return
        super().__setattr__(name, value)

    @property
    def _upgrade_defs(self):
        """Cache upgrade definitions to avoid repeated DB queries"""
        try:
            return object.__getattribute__(self, '_cached_defs')
        except AttributeError:
            try:
                cached_defs = {d.key: d for d in UpgradeDefinition.objects.all()}
            except Exception:
                cached_defs = {}
            object.__setattr__(self, '_cached_defs', cached_defs)
            return cached_defs

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

            val = getattr(self, field.name)
            # Skip if not a boolean or displacement field
            if not isinstance(val, (bool, int)):
                continue

            defn = defs.get(field.name)
            if defn:
                label = defn.description or defn.label
                points = defn.points
                if defn.per_unit and isinstance(val, int):
                    points = math.ceil(defn.per_unit * val)
            else:
                label = getattr(field, 'verbose_name', field.name)
                points = 0
                if field.name == 'displacement':
                    points = math.ceil(3.6 * val)

            # displacement is numeric; show its label, value and points
            if field.name == 'displacement':
                if val > 0:
                    installed += f"{label}: {val}% (+{points} pts)<br>"
                continue

            if val is True:
                installed += f"{label} (+{points} pts)<br>"
            elif val is False:
                not_installed += f"{label} ({points} pts)<br>"

    def upgrade_points(self):
        """Calculate total points from all enabled upgrades"""
        points = 0
        
        for key, definition in self._upgrade_defs.items():
            value = self.values.get(key, False if definition.per_unit is None else 0)
            
            if definition.per_unit is not None:
                # Numeric field like displacement
                try:
                    points += math.ceil(definition.per_unit * float(value))
                except (TypeError, ValueError):
                    pass
            else:
                # Boolean field
                try:
                    points += int(definition.points) * int(bool(value))
                except (TypeError, ValueError):
                    pass
                    
        return points
    

class UpgradesCreateForm(forms.ModelForm):
    class Meta:
        model = Upgrades
        fields = ['values']
        widgets = {
            'values': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Get all upgrade definitions, ordered by their display order
        try:
            definitions = UpgradeDefinition.objects.all().order_by('order', 'key')
        except Exception:
            definitions = []
            
        # Create a field for each upgrade definition
        for definition in definitions:
            field_value = (instance.values.get(definition.key, False) 
                         if instance and instance.values else False)
            
            if definition.per_unit is not None:
                # Numeric field (like displacement)
                self.fields[definition.key] = forms.IntegerField(
                    label=definition.description,
                    help_text=f"Points: {definition.per_unit} × value",
                    required=False,
                    initial=field_value,
                    min_value=0,
                    max_value=100
                )
            else:
                # Boolean field
                self.fields[definition.key] = forms.BooleanField(
                    label=definition.description,
                    help_text=f"Points: {int(definition.points)}",
                    required=False,
                    initial=field_value
                )
            
            # Apply Bootstrap styling
            self.fields[definition.key].widget.attrs['class'] = 'form-control'
            
    def clean(self):
        """Store all the dynamic field values in the values JSONField"""
        cleaned_data = super().clean()
        values = {}
        
        # Collect values from all dynamic fields
        for key in list(cleaned_data.keys()):
            if key != 'values':  # Skip the actual JSONField
                values[key] = cleaned_data.pop(key)
        
        cleaned_data['values'] = values
        return cleaned_data