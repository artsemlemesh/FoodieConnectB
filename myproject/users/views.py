from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, UpdateView
from myproject import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import LoginView, PasswordChangeView
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm




class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'authorization'}


    def get_success_url(self):
        return reverse_lazy('users:profile')#CHANGE REDIRECT TO THE MAIN PAGE (ALSO KNOWN AS A HOMEPAGE)
    

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'registration'}
    success_url = reverse_lazy('users:login')


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'profile of the user',
                     'default_image': settings.DEFAULT_USER_IMAGE}
    

    def get_success_url(self):
        return reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


