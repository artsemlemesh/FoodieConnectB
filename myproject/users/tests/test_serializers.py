from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from users.serializers import (
    LoginSerializer, 
    RegisterSerializer, 
    ProfileSerializer, 
    PasswordChangeSerializer,
    CustomTokenObtainPairSerializer
)

class SerializerTests(APITestCase):
    def test_register_serializer(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "password123",
            "password2": "password123"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, data["username"])
        self.assertTrue(user.check_password(data["password1"]))

    def test_login_serializer(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="password123")
        data = {"username": "testuser", "password": "password123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_profile_serializer(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", email="test@example.com")
        serializer = ProfileSerializer(user, data={"username": "updateduser"})
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, "updateduser")

    def test_password_change_serializer(self):
        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="password123")
        context = {"request": type("Request", (), {"user": user})}
        serializer = PasswordChangeSerializer(
            data={"old_password": "password123", "new_password": "newpassword123"},
            context=context,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(user.check_password("newpassword123"))