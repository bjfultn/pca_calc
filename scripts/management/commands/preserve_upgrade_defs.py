from django.core.management.base import BaseCommand
import json
from db.models import Upgrades

class Command(BaseCommand):
    help = 'Export all current Upgrades field definitions to a JSON file for preservation'

    def handle(self, *args, **options):
        definitions = []
        model = Upgrades
        
        for field in model._meta.get_fields():
            # Skip non-upgrade fields like id and car
            if field.name in ['id', 'car']:
                continue
            
            # Get the verbose name if it exists
            verbose_name = getattr(field, 'verbose_name', field.name)
            
            # Extract the points value from the verbose_name if it exists
            points = 0
            if '(' in verbose_name and 'points' in verbose_name.lower():
                try:
                    points_text = verbose_name[verbose_name.rindex('(')+1:verbose_name.rindex(')')]
                    if 'points' in points_text:
                        points = float(points_text.split()[0])
                except:
                    pass
            
            # Special handling for displacement
            per_unit = None
            if field.name == 'displacement':
                per_unit = 3.6
                points = 0
            
            # Create definition entry
            definition = {
                'key': field.name,
                'label': field.name.replace('_', ' ').title(),
                'description': verbose_name,
                'points': points,
                'per_unit': per_unit,
                # Group fields roughly by category
                'order': self.get_field_order(field.name)
            }
            
            definitions.append(definition)
        
        # Save to a JSON file
        output_path = 'upgrade_definitions.json'
        with open(output_path, 'w') as f:
            json.dump(definitions, f, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {len(definitions)} upgrade definitions to {output_path}')
        )
    
    def get_field_order(self, field_name):
        """Group fields by category for nice ordering"""
        categories = {
            # Engine mods
            'engine': ['mid_engine', 'induction', 'engine_head', 'camshaft', 
                      'forced_induction', 'boost', 'displacement'],
            # Exhaust
            'exhaust': ['muffler', 'cats', 'headers'],
            # Drivetrain
            'drivetrain': ['differential', 'final_drive', 'pdk'],
            # Suspension
            'suspension': ['shocks', 'shock_tower', 'factory_springs', 
                         'aftermarket_springs', 'fixed_sway', 'adj_sway',
                         'custom_suspension', 'camber', 'spherical_bearings'],
            # Chassis/Body
            'chassis': ['tube_frame', 'factory_aero', 'oem_aero', 
                       'aftermarket_aero', 'windshield_delete'],
            # Other
            'other': ['brakes', 'traction_control']
        }
        
        # Find which category the field belongs to
        for order, (category, fields) in enumerate(categories.items()):
            if field_name in fields:
                # Within each category, preserve the order listed above
                return order * 100 + fields.index(field_name)
        
        return 999  # Default order for any uncategorized fields