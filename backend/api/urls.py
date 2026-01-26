from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserAvatarView,
    UserViewSet,
)

router = DefaultRouter()
router.register('custom_users', UserViewSet, basename='custom-users')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('users/me/avatar/', UserAvatarView.as_view()),
    path('', include(router.urls)),
    path('users/', include('djoser.urls')),
    path('users/', include('djoser.urls.authtoken')),
]

