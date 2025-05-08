from django.contrib import admin
from django.urls import include, path, re_path
from . import views
from users import views as user_views

urlpatterns = [
    path(r'', views.home),
    path(r'user/', include('users.urls')),
    path(r'user/', include('django.contrib.auth.urls')),
    path(r'admin/', admin.site.urls),
    path(r'explorer/', include('explorer.urls')),
    path(r'api/', include('api.urls')),
    path(r'garage/', views.garage),
    path(r'competition/', views.competition),
    path(r'garage/add/', views.add_car),
    path(r'garage/edit/<int:carid>/', views.edit_car),
    path(r'garage/edit/<int:carid>/delete/', views.delete_car),
    path(r'garage/edit/<int:carid>/tires/', views.edit_tire),
    path(r'garage/edit/<int:carid>/upgrades/', views.edit_upgrades),
    path(r'garage/view/<int:carid>/', views.view_car),
    path(r"select2/", include("django_select2.urls")),
]
