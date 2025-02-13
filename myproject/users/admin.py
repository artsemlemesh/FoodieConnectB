from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = User
    # Define fieldsets to organize fields in the admin form
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('photo', 'data_birth', 'is_premium')}),
    )

    # Define add_fieldsets to include custom fields when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('photo', 'data_birth', 'is_premium')}),
    )



admin.site.register(User, CustomUserAdmin) #check

