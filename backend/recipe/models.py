from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import (
    Exists,
    OuterRef,
    Value,
    BooleanField
)

from .constants import (
    MEASUREMENT_MAX_LENGTH,
    RECIPES_MAX_LENGTH,
    MIN_AMOUNT,
    TAG_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название')
    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True)

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Тег'
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'




class RecipeQuerySet(models.QuerySet):
    def with_user_flags(self, user):
        if not user.is_authenticated:
            return self.annotate(
                is_favorited=Value(
                    False, output_field=BooleanField()
                ),
                is_in_shopping_cart=Value(
                    False, output_field=BooleanField()
                ),
            )

        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=user,
                    recipe=OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):
    name = models.CharField(
        max_length=RECIPES_MAX_LENGTH,
        verbose_name='Название')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        verbose_name='Фото'
    )
    text = models.TextField(
        verbose_name='Рецепт'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Время готовки'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепт'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты рецепта'
        verbose_name = 'Ингредиент рецепта'
        ordering = ('recipe', 'ingredient__name')

    def __str__(self):
        return (
            f'{self.ingredient.name} — {self.amount} '
            f'{self.ingredient.measurement_unit} '
            f'в рецепте "{self.recipe.name}"'
        )


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(app_label)s_%(class)s'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(app_label)s_%(class)s'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(app_label)s_%(class)s'
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.recipe}'


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user} добавил в корзину "{self.recipe}"'


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил в избранное "{self.recipe}"'
