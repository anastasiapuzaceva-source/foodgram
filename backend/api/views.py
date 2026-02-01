from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .permission import IsAuthorOrReadOnly
from .serializers import (
    RecipeReadSerializer,
    CreateRecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    UserAvatarSerializer,
    UserSubscriptionSerializer,
    ShoppingCartSerializer,
    RecipeShortSerializer,
    FavoriteRecipeSerializer
)
from recipe.models import (
    Tag, Ingredient, Recipe,
    ShoppingCart, RecipeIngredient, Favorite
)
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = 'pk'


    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                request.user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted_count, _ = Subscription.objects.filter(
            user=user,
            author=author
        ).delete()
        if deleted_count == 0:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(
            subscribers__user=user
        )
        page = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeReadSerializer

    def _add_or_remove(
            self,
            request,
            pk,
            model,
            serializer_class,
            error_message
    ):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            serializer = serializer_class(
                data={'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(
                RecipeShortSerializer(
                    recipe, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        deleted, _ = model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()

        if not deleted:
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(
            request=request,
            pk=pk,
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
            error_message='Рецепта нет в корзине покупок'
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._add_or_remove(
            request=request,
            pk=pk,
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
            error_message='Рецепта нет в корзине покупок'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__recipe_shoppingcart__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        lines = [
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) — "
            f"{item['total_amount']}"
            for item in ingredients
        ]
        content = '\n'.join(lines)
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': short_link})

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove(
            request=request,
            pk=pk,
            model=Favorite,
            serializer_class=FavoriteRecipeSerializer,
            error_message='Рецепта нет в избранном'
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._add_or_remove(
            request=request,
            pk=pk,
            model=Favorite,
            serializer_class=FavoriteRecipeSerializer,
            error_message='Рецепта нет в избранном'
        )
