from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewsTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_register_user(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "password123",
            "password2": "password123"
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)

    def test_login_user(self):
        response = self.client.post(
            "/users/token/", {"username": "testuser", "password": "password123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    # def test_profile_update(self):
    #     data = {"username": "updateduser"}
    #     response = self.client.put("/users/profile/", data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["username"], "updateduser")

    # def test_password_change(self):
    #     data = {"old_password": "password123", "new_password": "newpassword123"}
    #     response = self.client.put("/users/password-change/", data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list(self):
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_logout_user(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post("/users/logout/", {"refresh_token": refresh})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)