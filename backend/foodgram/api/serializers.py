from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, User
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.hashers import make_password


class CustomCreateUserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'Пароль', 'placeholder': 'Пароль'}
    )

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(CustomCreateUserSerializers, self).create(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'tags', 'image', 'text', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
