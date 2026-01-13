from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from users.models import User
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from db.models import *


import datetime

admin.site.site_header = 'Administration'
admin.site.index_title = 'Home'
admin.site.site_title = 'Admin'

admin.site.unregister(Group)
admin.site.unregister(Site)


UserAdmin.list_display = ['username', 'email', 'name', 'last_login',
                          'is_active', 'is_staff', 'is_superuser',
                          'comment'
                          ]

UserAdmin.fieldsets = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'comment')}),
    ('Permissions',
        {'fields': ('is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')})
    )

UserAdmin.exclude = ['password']

admin.site.register(Site)
admin.site.register(User, UserAdmin)


@admin.register(Tire)
class TireAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'get_user', 'front_section_width', 'rear_section_width', 
                    'race_tires', 'autox_tires', 'street_tires', 'tire_points']
    list_filter = ['race_tires', 'autox_tires', 'street_tires']
    search_fields = ['car__user__username', 'car__user__email', 'car__make', 'car__model']
    
    def get_user(self, obj):
        if obj.car and obj.car.user:
            return obj.car.user.username
        return '-'
    get_user.short_description = 'User'
    get_user.admin_order_field = 'car__user__username'


@admin.register(Upgrades)
class UpgradesAdmin(admin.ModelAdmin):
    list_display = ['get_label', 'get_car_label', 'get_user', 'upgrade_points']
    search_fields = ['car__user__username', 'car__user__email', 'car__make', 'car__model']
    
    def get_label(self, obj):
        """Return the upgrade instance label (same as __str__) as a clickable link."""
        url = reverse('admin:db_upgrades_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj))
    get_label.short_description = 'Label'
    get_label.admin_order_field = 'id'
    
    def get_car_label(self, obj):
        if obj.car:
            url = reverse('admin:db_car_change', args=[obj.car.pk])
            return format_html('<a href="{}">{}</a>', url, str(obj.car))
        return '-'
    get_car_label.short_description = 'Car'
    get_car_label.admin_order_field = 'car'
    
    def get_user(self, obj):
        if obj.car and obj.car.user:
            return obj.car.user.username
        return '-'
    get_user.short_description = 'User'
    get_user.admin_order_field = 'car__user__username'


admin.site.register(Car)
admin.site.register(UpgradeDefinition)
