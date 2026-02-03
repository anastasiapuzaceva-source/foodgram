from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__email', 'author__email')
    list_filter = ('user', 'author')


admin.site.unregister(Group)
