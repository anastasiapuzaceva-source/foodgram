from django_filters.rest_framework import (
    BooleanFilter,
    FilterSet,
    CharFilter,
    ModelMultipleChoiceFilter,
)
from django.shortcuts import get_object_or_404

from recipe.models import Ingredient, Recipe, Tag

User = get_object_or_404


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter()
    is_in_shopping_cart = BooleanFilter()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
