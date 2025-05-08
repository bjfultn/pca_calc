from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from users.models import User
from django.utils import timezone
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

admin.site.register(Car)
admin.site.register(Tire)
admin.site.register(Upgrades)
