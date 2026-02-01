from django.contrib import admin
from django.db.models import Count

from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    ShoppingCart,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    search_fields = ('author__username', 'name')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(favorites_total=Count('recipe_favorite'))

    @admin.display(
        description='Количество добавлений в избранное',
        ordering='favorites_total'
    )
    def favorites_count(self, obj):
        return obj.favorites_total


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag)
