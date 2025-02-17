from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


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


    #no need probably
    # @property
    # def has_active_subscription(self):
    #     subscription = getattr(self, 'subscription', None)
    #     return subscription and subscription.is_active()

    #access User model- get_user_model(), in settings add AUTH_USER_MODEL = "users.User" where users is an app name


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One subscription per user
    plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE)  # Link to SubscriptionPlan
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)  # Optional if no end date
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
    
    def is_active(self):
        #true if its still active
        if self.end_date and self.end_date < now() and self.active:
            self.active = False
            self.save(update_fields=['active'])
            return False
        return self.active


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name