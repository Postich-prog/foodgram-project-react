from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, CustomUserViewSet)

app_name = 'api'
router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)

router.register(r'recipes/(?P<recipe_id>\d+)/', RecipeViewSet)
router.register(r'users/(?P<user_id>\d+)/', CustomUserViewSet)
router.register(r'tags/(?P<tag_id>\d+)/', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
