from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, null=True, verbose_name='photo')
    data_birth = models.DateTimeField(blank=True, null=True, verbose_name='date of birth')
     # Override the related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='mygroups',  # Change this to a unique name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='mypermissions',  # Change this to a unique name
        blank=True,
    )
    is_premium = models.BooleanField(default=False)



    #access User model- get_user_model(), in settings add AUTH_USER_MODEL = "users.User" where users is an app name