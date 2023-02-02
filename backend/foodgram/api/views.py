from rest_framework import filters, permissions, status, viewsets, generics
from rest_framework.pagination import PageNumberPagination
from recipes.models import Recipe, Tag, Ingredient, User
from .serializers import (RecipeSerializer, TagSerializer,
                          IngredientSerializer, UserSerializer,
                          GetTokenSerializer, SignupSerializer)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'], url_path='me',
        detail=False, permission_classes=(permissions.IsAuthenticated,)
    )
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if request.user.is_user or request.user.is_moderator:
                if serializer.validated_data.get('role') != request.user.role:
                    serializer.save(role=request.user.role)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class APIGetToken(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if (
            serializer.validated_data[
                'confirmation_code'
            ] == user.confirmation_code
        ):
            token = RefreshToken.for_user(user).access_token
            return Response(
                {'Token': str(token)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'Неправильный confirmation_code'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APISignup(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid() and request.data['username'] != 'me':
            user = serializer.save()
            send_mail(
                'Код подтверждения',
                f'Ваш логин: {user.username} и confirmation_code: '
                f'{user.confirmation_code}',
                'no_reply@yamdb.ru',
                [user.email],
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
