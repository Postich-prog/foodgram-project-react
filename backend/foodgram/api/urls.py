from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet
)

app_name = 'api'
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
