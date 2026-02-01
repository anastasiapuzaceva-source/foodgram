from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipe.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    ShoppingCart,
    Favorite,
    UserRecipeRelation
)

from .fields import Base64ImageField

User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()

    def get_shopping_cart_count(self, obj):
        return obj.shopping_cart.count()


class UserCreateSerializer(DjoserUserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'validators': []},
            'username': {'validators': []},
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if not bool(re.match(r'^[\w.@+-]+$', value)):
            raise serializers.ValidationError(
                'Поле содержит недопустимые символы'
            )

        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать username "me" запрещено.'
            )

class UserSubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'avatar',
            'is_subscribed'
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'ingredients',
            'tags',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужно указать хотя бы один ингредиент.'
            })
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно указать хотя бы один тег.'
            })
        ingredient_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.'
            })
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Теги не должны повторяться.'
            })
        return data

    def _create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )
            for item in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.ingredients.clear()
            self._create_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_image(self, obj):
        return obj.image.url

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
                request
                and request.user.is_authenticated
                and Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
                request
                and request.user.is_authenticated
                and ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок'
            )
        return attrs


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return attrs
