from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, UpdateView
from myproject import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import LoginView, PasswordChangeView
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer, RegisterSerializer, ProfileSerializer, PasswordChangeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import api_view

class LoginUser(APIView):  # Change to APIView for API handling
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            # You can return user data or a token here
            photo_url = None
            if user.photo:
                photo_url = f"{request.build_absolute_uri(settings.MEDIA_URL)}{user.photo.name}"

            return Response({
                "message": "Login successful",
                "username": user.username,
                "photo": photo_url  # Return the photo URL or None if not set
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # You can return a simple message or a form if needed
        return Response({"message": "Please provide your username and password to log in."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


class RegisterUser(generics.CreateAPIView):
    # form_class = RegisterUserForm   #those are for html templates
    # template_name = 'users/register.html'
    serializer_class = RegisterSerializer
    # extra_context = {'title': 'registration'} # no need
    success_url = reverse_lazy('users:login') # check later


class ProfileUser(LoginRequiredMixin, generics.UpdateAPIView):
    # model = get_user_model()
    # form_class = ProfileUserForm
    # template_name = 'users/profile.html'
    # extra_context = {'title': 'profile of the user',
    #                  'default_image': settings.DEFAULT_USER_IMAGE}
    

    # def get_success_url(self):
    #     return reverse_lazy('users:profile')
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all() #probably returns all the users, 


    def get_object(self, queryset=None):
        return self.request.user # updates the logged in user profile
    

class UserPasswordChange(LoginRequiredMixin, generics.UpdateAPIView):
    # form_class = UserPasswordChangeForm
    # success_url = reverse_lazy('users:password_change_done')
    # template_name = 'users/password_change_form.html'

    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user #changes the password for the logged in user
    

    def perform_update(self, serializer):
        serializer.save()  #calls the save method to change the password


