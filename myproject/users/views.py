from django.urls import reverse, reverse_lazy
from django.contrib.auth import  login, logout, get_user_model
from django.http import  HttpResponseRedirect
from myproject import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer, RegisterSerializer, ProfileSerializer, PasswordChangeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny


# login view 
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




# class LoginUser(APIView):  # Change to APIView for API handling
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             login(request, user)
#             # You can return user data or a token here
#             photo_url = None
#             if user.photo:
#                 photo_url = f"{request.build_absolute_uri(settings.MEDIA_URL)}{user.photo.name}"

#             return Response({
#                 "message": "Login successful",
#                 "username": user.username,
#                 "photo": photo_url  # Return the photo URL or None if not set
#             }, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request):
#         # You can return a simple message or a form if needed
#         return Response({"message": "Please provide your username and password to log in."}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def logout_user(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('users:login'))



class LogoutView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Invalid or already blacklisted token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterUser(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  
        
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "photo": user.photo.url if user.photo else None,  
            }
        }, status=status.HTTP_201_CREATED)
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


