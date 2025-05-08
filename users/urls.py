from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.SignUp.as_view(), name='sign_up'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.haml'), name='login'),
    path('password_change/', views.PasswordChange, name='password_change'),
]
