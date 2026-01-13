from django.core.management.base import BaseCommand
from db.models.upgrades import Upgrades
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate Upgrades entries, keeping only one per car_id.'

    def handle(self, *args, **options):
        duplicates = (
            Upgrades.objects.values('car_id')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        total_removed = 0
        for dup in duplicates:
            car_id = dup['car_id']
            upgrades = Upgrades.objects.filter(car_id=car_id).order_by('id')
            # Keep the first, delete the rest
            to_delete_ids = list(upgrades.values_list('id', flat=True))[1:]
            count = len(to_delete_ids)
            if count > 0:
                Upgrades.objects.filter(id__in=to_delete_ids).delete()
                total_removed += count
                self.stdout.write(f"Removed {count} duplicate(s) for car_id {car_id}")
        self.stdout.write(self.style.SUCCESS(f"Cleanup complete. Total removed: {total_removed}"))
