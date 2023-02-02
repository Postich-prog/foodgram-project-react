from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet,
    APIGetToken, APISignup
)

app_name = 'api'
router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('/auth/token/', APIGetToken.as_view()),
    path('/auth/signup/', APISignup.as_view())
]
