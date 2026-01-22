from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Ingredient,
    ShoppingCart,
    RecipeIngredient,
)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    search_fields = ('author__username', 'name')
    inlines = (RecipeIngredientInline,)
    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'Количество добавлений в избранное'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

admin.site.register(Tag)
