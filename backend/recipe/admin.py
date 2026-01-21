from django.contrib import admin
from .models import User

from .models import (
    Tag,
    Recipe,
    Ingredient,
    ShoppingCart,
    UserAvatar,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    filter_horizontal = ('tags',)
    search_fields = ('author__username', 'name')
    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'Количество добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShoppingCart)
admin.site.register(UserAvatar)