from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserAvatar


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username')


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ('user',)
