# no, for these models:from django.db import models
# from django.contrib.auth.models import AbstractUser


# class User(AbstractUser):
#     photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True, verbose_name='photo')
#     data_birth = models.DateTimeField(blank=True, null=True, verbose_name='date of birth')
#      # Override the related_name for groups and user_permissions
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='mygroups',  # Change this to a unique name
#         blank=True,
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='mypermissions',  # Change this to a unique name
#         blank=True,
#     )


#     #access User model- get_user_model(), in settings add AUTH_USER_MODEL = "users.User" where users is an app name
# then for theses serializers.py:
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from myproject import settings




# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)

#         # Add custom fields
#         user = self.user
#         data['username'] = user.username
#         data['photo'] = None
#         data['is_admin'] = user.is_staff
#         data['id'] = user.id
#         if user.photo:
#             data['photo'] = f"{self.context['request'].build_absolute_uri(settings.MEDIA_URL)}{user.photo.name}"
#         return data



# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = get_user_model()
#         fields = '__all__'


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, attrs):
#         # Authenticate the user
#         user = authenticate(username=attrs['username'], password=attrs['password'])
#         if user is None:
#             raise serializers.ValidationError("Invalid username or password.")

#         # Generate tokens
#         refresh = RefreshToken.for_user(user)
#         attrs['user'] = user
#         attrs['refresh'] = str(refresh)
#         attrs['access'] = str(refresh.access_token)

#         return attrs


# class RegisterSerializer(serializers.ModelSerializer):
#     password1 = serializers.CharField(write_only = True)
#     password2 = serializers.CharField(write_only = True)
#     is_admin = serializers.BooleanField(source='is_staff', read_only=True) 
    
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'password1', 'password2', 'is_admin']

#     def validate(self, attrs):
#         if attrs['password1'] != attrs['password2']:
#             raise serializers.ValidationError('Passwords dont match')
#         return attrs
    
#     def create(self, validated_data):
#         user = get_user_model()(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )
#         user.set_password(validated_data['password1'])
#         user.save()
#         return user
    

# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ['username', 'email', 'photo', 'data_birth']

#     def update(self, instance, validated_data):
#         instance.username = validated_data.get('username', instance.username)
#         instance.email = validated_data.get('email', instance.email)
#         instance.photo = validated_data.get('photo', instance.photo)
#         instance.data_birth = validated_data.get('data_birth', instance.data_birth)
#         instance.save()
#         return instance
    

# class PasswordChangeSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)

#     def validate_old_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError("Old password is incorrect.")
#         return value
    
#     def validate(self, attrs):
#         if attrs['old_password'] == attrs['new_password']:
#             raise serializers.ValidationError("New password must be different from the old password.")
#         return attrs
    
#     def save(self):
#         user = self.context['request'].user
#         user.set_password(self.validated_data['new_password'])
#         user.save()
# and urls.py


# from django.urls import path, reverse_lazy
# from .views import RegisterUser, LogoutView, ProfileUser, UserPasswordChange, CustomTokenObtainPairView, UserListView

# from django.contrib.auth.views import PasswordChangeDoneView, PasswordResetDoneView, \
#     PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView

# from rest_framework_simplejwt.views import  TokenRefreshView 

# app_name = 'users'

# urlpatterns = [
#     path('logout/', LogoutView.as_view(), name='logout'),

#     path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('password-change/', UserPasswordChange.as_view(), name='password_change'),
#     path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),


#     path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html',
#                                                       email_template_name='users/password_reset_email.html',
#                                                       success_url=reverse_lazy('users:password_reset_done')), name='password_reset'),
#     path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),#the views are built-in, but templates are our own, slightly customized, url names should be exactly the same
#     path('password-reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
#                                                                              success_url=reverse_lazy('users:password_reset_complete')),name='password_reset_confirm'),        
#     path('password-reset/complete/',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),

#     path('register/', RegisterUser.as_view(), name='register'),
#     path('profile/', ProfileUser.as_view(), name='profile'),
#     path('users/', UserListView.as_view(), name='user-list'),                                                                                                    
# ]

# and views:
# from django.urls import reverse, reverse_lazy
# from django.contrib.auth import  login, logout, get_user_model
# from django.http import  HttpResponseRedirect
# from myproject import settings
# from django.contrib.auth.mixins import LoginRequiredMixin
# from rest_framework.permissions import IsAuthenticated
# from .serializers import LoginSerializer, RegisterSerializer, ProfileSerializer, PasswordChangeSerializer, UserSerializer
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import generics
# from rest_framework.decorators import api_view
# from rest_framework_simplejwt.tokens import RefreshToken  
# from rest_framework_simplejwt.views import TokenObtainPairView
# from .serializers import CustomTokenObtainPairSerializer
# from rest_framework_simplejwt.exceptions import TokenError
# from rest_framework.permissions import AllowAny


# # login view 
# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer




# # class LoginUser(APIView):  # Change to APIView for API handling
# #     def post(self, request):
# #         serializer = LoginSerializer(data=request.data)
# #         if serializer.is_valid():
# #             user = serializer.validated_data['user']
# #             login(request, user)
# #             # You can return user data or a token here
# #             photo_url = None
# #             if user.photo:
# #                 photo_url = f"{request.build_absolute_uri(settings.MEDIA_URL)}{user.photo.name}"

# #             return Response({
# #                 "message": "Login successful",
# #                 "username": user.username,
# #                 "photo": photo_url  # Return the photo URL or None if not set
# #             }, status=status.HTTP_200_OK)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# #     def get(self, request):
# #         # You can return a simple message or a form if needed
# #         return Response({"message": "Please provide your username and password to log in."}, status=status.HTTP_200_OK)


# # @api_view(['POST'])
# # def logout_user(request):
# #     logout(request)
# #     return HttpResponseRedirect(reverse('users:login'))



# class LogoutView(APIView):
#     permission_classes = [AllowAny]  # No authentication required

#     def post(self, request):
#         refresh_token = request.data.get('refresh_token')
#         if not refresh_token:
#             return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
#         except TokenError:
#             return Response({"detail": "Invalid or already blacklisted token"}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class RegisterUser(APIView):
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save() 
#         refresh = RefreshToken.for_user(user)
#         access = refresh.access_token

#         return Response({
#             "access": str(access),
#             "refresh": str(refresh),
#             "user": {
#                 "username": user.username,
#                 "photo": user.photo.url if user.photo else None, 
#                 "is_admin": user.is_staff  
#             }
#         }, status=status.HTTP_201_CREATED)
    
# class ProfileUser(LoginRequiredMixin, generics.UpdateAPIView):
    
#     serializer_class = ProfileSerializer
#     queryset = get_user_model().objects.all() #probably returns all the users, 


#     def get_object(self, queryset=None):
#         return self.request.user # updates the logged in user profile
    

# class UserListView(generics.ListAPIView):
#     queryset = get_user_model().objects.all()
#     serializer_class = UserSerializer


# class UserPasswordChange(LoginRequiredMixin, generics.UpdateAPIView):
#     # form_class = UserPasswordChangeForm
#     # success_url = reverse_lazy('users:password_change_done')
#     # template_name = 'users/password_change_form.html'

#     serializer_class = PasswordChangeSerializer

#     def get_object(self):
#         return self.request.user #changes the password for the logged in user
    

#     def perform_update(self, serializer):
#         serializer.save()  #calls the save method to change the password


