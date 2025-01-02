from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
from datetime import datetime
from users.models import User

class TestUserModel(TestCase):
    def test_create_user_with_photo(self):
        photo = SimpleUploadedFile("photo.jpg", b"file_content", content_type="image/jpeg")
        user = User.objects.create_user(
            username="photouser",
            email="photouser@example.com",
            password="password123",
            photo=photo
        )
        assert user.photo.name.startswith("users/")
        assert "photo" in user.photo.name  # Check for "photo" in the filename

    def test_groups_and_permissions_related_name(self):
        user = User.objects.create_user(username="groupuser", password="password123")
        assert hasattr(user, "groups")  # Default related name

    def test_create_user_with_data_birth(self):
        data_birth = make_aware(datetime(1990, 1, 1))
        user = User.objects.create_user(
            username="testuser",
            password="password123",
            data_birth=data_birth
        )
        assert user.data_birth == data_birth