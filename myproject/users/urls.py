

from django.urls import path, reverse_lazy
from .views import RegisterUser, LogoutView, ProfileUser, UserPasswordChange, \
      CustomTokenObtainPairView, UserListView, UserDetailView

from django.contrib.auth.views import PasswordChangeDoneView, PasswordResetDoneView, \
    PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView

from rest_framework_simplejwt.views import  TokenRefreshView 

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),

    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-change/', UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),


    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                                      email_template_name='users/password_reset_email.html',
                                                      success_url=reverse_lazy('users:password_reset_done')), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),#the views are built-in, but templates are our own, slightly customized, url names should be exactly the same
    path('password-reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                                                             success_url=reverse_lazy('users:password_reset_complete')),name='password_reset_confirm'),        
    path('password-reset/complete/',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),

    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),                                                                                                    
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-list'),                                                                                                    
]
