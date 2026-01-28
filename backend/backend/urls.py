from django.contrib import admin
from django.urls import path, include

from api.views import UserViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/users/<int:pk>/',
        UserViewSet.as_view({'get': 'retrieve'}),
    ),
    path(
        'api/users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
    ),
    path(
        'api/users/<int:pk>/subscribe/',
        UserViewSet.as_view({
            'post': 'subscribe',
            'delete': 'subscribe',
        }),
    ),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    path('api/', include('api.urls')),
]
