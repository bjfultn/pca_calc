from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.forms import ValidationError

class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
