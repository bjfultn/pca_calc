from django.urls import path
from . import views

urlpatterns = [
    path('settings/<key>', views.user_settings),
    path('competition/', views.competition),
    path('database_backup/', views.database_backup)
]
