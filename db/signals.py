from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Car, Tire, Upgrades


@receiver(pre_save, sender=Car)
def update_car_timestamp_on_save(sender, instance, **kwargs):
    """Update the car's last_updated timestamp when the car itself is saved."""
    # Update timestamp whenever a car is saved (new or existing)
    instance.last_updated = timezone.now()


@receiver(post_save, sender=Tire)
def update_car_timestamp_from_tire(sender, instance, **kwargs):
    """Update the car's last_updated timestamp when a tire is saved."""
    if instance.car:
        # Use update() to avoid triggering save signals recursively
        Car.objects.filter(id=instance.car.id).update(last_updated=timezone.now())


@receiver(post_save, sender=Upgrades)
def update_car_timestamp_from_upgrade(sender, instance, **kwargs):
    """Update the car's last_updated timestamp when an upgrade is saved."""
    if instance.car:
        # Use update() to avoid triggering save signals recursively
        Car.objects.filter(id=instance.car.id).update(last_updated=timezone.now())

