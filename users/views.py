from django.contrib import messages
from django.views import generic
from .forms import UserCreationForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse

class SignUp(SuccessMessageMixin, generic.CreateView):
    form_class = UserCreationForm
    success_url = '/user/login'
    success_message = 'Your account was created!'
    template_name = 'users/sign_up.haml'

class Profile(SuccessMessageMixin, generic.UpdateView):
    form_class = UserChangeForm
    success_url = '/user/profile'
    success_message = 'Your profile was successfully updated!'
    template_name = 'users/profile.haml'
    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def PasswordChange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/user/profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/password_change.haml', {
        'form': form
    })

