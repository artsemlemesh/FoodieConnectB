from django.urls import reverse, reverse_lazy
from django.contrib.auth import  login, logout, get_user_model
from django.http import  HttpResponseRedirect
from myproject import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer, RegisterSerializer, ProfileSerializer, PasswordChangeSerializer, UserSerializer
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
from rest_framework.generics import RetrieveDestroyAPIView
from .models import Subscription, SubscriptionPlan
from django.utils import timezone 
from datetime import timedelta
from .serializers import SubscriptionSerializer, SubscriptionPlanSerializer
# login view 
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(RetrieveDestroyAPIView):
    """
    Retrieve or delete a specific user by ID.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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


from django.core.cache import caches
import logging
logger = logging.getLogger(__name__)
ONLINE_USERS_KEY = "online_users"
class LogoutView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Remove user from online status
            user_id = request.user.id

            logger.info(f"User {user_id} IDENTIFIED")
            cache = caches['page_view_cache']

            if user_id:
                cache.delete(f'{ONLINE_USERS_KEY}:{user_id}')
                logger.info(f"User {user_id} removed from online users.")

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
                "is_admin": user.is_staff,
                "is_premium": user.is_premium
            }
        }, status=status.HTTP_201_CREATED)
    
class ProfileUser(LoginRequiredMixin, generics.UpdateAPIView):
    
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all() #probably returns all the users, 


    def get_object(self, queryset=None):
        return self.request.user # updates the logged in user profile
    

class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserPasswordChange(LoginRequiredMixin, generics.UpdateAPIView):
    # form_class = UserPasswordChangeForm
    # success_url = reverse_lazy('users:password_change_done')
    # template_name = 'users/password_change_form.html'

    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user #changes the password for the logged in user
    

    def perform_update(self, serializer):
        serializer.save()  #calls the save method to change the password


class SubscriptionPlanListView(generics.ListAPIView):
    """Returns a list of available subscription plans from the database."""
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

class SubscribeView(generics.GenericAPIView):
    """Allows the user to subscribe to a plan."""
    # permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'You must be logged in to subscribe'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            subscription = Subscription.objects.get(user=user)
            if subscription.is_active():
                return Response({'error': 'You already have an active subscription'}, status=status.HTTP_400_BAD_REQUEST)
        except Subscription.DoesNotExist:
            pass

        plan_id = request.data.get('plan')

        if not plan_id:
            return Response({'error': 'Plan is required'}, status=status.HTTP_400_BAD_REQUEST)

       
        try:
            plan_id = int(plan_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except ValueError:
            return Response({'error': 'Invalid plan ID'}, status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30), #1 month subscription
                'active': True
            }
            )
        if not created:
            subscription.plan = plan
            subscription.start_date = timezone.now()
            subscription.end_date = timezone.now() + timedelta(days=30)
            subscription.active = True
            subscription.save()

        return Response({'message': f'Subscribed to {plan.name} plan'}, status=status.HTTP_200_OK)
        

class SubscriptionStatusView(generics.RetrieveAPIView):
    """Returns the current subscription status of the authenticated user."""
    # permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user)
            subscription.is_active()
            return Response({
                'plan': subscription.plan.name,
                'active': subscription.active,
                'start_date': subscription.start_date,
                'end_date': subscription.end_date
            })
        except Subscription.DoesNotExist:
            return Response({'status': 'No active subscription'}, status=404)