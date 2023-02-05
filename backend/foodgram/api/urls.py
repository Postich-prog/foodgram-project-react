from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet
)

app_name = 'api'
router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
