from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Unregister the original User admin
admin.site.unregister(User)

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    # Add or remove fields to customize what's displayed in the admin panel

# Re-register User with the new admin class
admin.site.register(User, UserAdmin)



