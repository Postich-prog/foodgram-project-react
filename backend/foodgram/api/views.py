from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import FilterSet, filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

from .permissions import (IsAdminModeratorAuthorOrReadOnly,
                          IsAdminOrSuperuserOrReadOnly)
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             queryset=Tag.objects.all(),
                                             to_field_name='slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=user, author=author)
            queryset = Follow.objects.get(user=request.user, author=author)
            serializer = FollowSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilter
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(
                    user=user,
                    recipe=get_object_or_404(Recipe, id=pk)
                )
                queryset = Favorite.objects.get(
                    user=user,
                    recipe=get_object_or_404(Recipe, id=pk)
                )
                serializer = FavoriteSerializer(
                    queryset,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        with open("shopping_cart.txt", "w") as file:
            for ingredient in ingredients:
                file_list.add(ingredient)
            print(*file_list, file=file)
        return file


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)
    pagination_class = None
