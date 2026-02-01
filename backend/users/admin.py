from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username')


admin.site.unregister(Group)
