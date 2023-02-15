import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'Пароль', 'placeholder': 'Пароль'}
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_anonymous and Follow.objects.filter(
            user=user,
            author=obj.id
        ).exists()

    def validate(self, obj):
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Вы не можете использовать этот username.'}
            )
        return obj


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializers(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def exists_func(self, obj, model):
        user = self.context.get('request').user
        return user.is_anonymous and model.objects.filter(
            user=user,
            recipe=obj.id
        ).exists()

    def get_is_favorited(self, obj):
        return RecipeSerializer.exists_func(self, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return RecipeSerializer.exists_func(self, obj, ShoppingCart)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = {}
        if ingredients:
            for ingredient in ingredients:
                if ingredient.get('id') in ingredients_list:
                    raise ValidationError(
                        'Ингредиент должен быть уникальным')
                if int(ingredient.get('amount')) <= 0:
                    raise ValidationError(
                        'Добавьте количество для ингредиента больше 0'
                    )
                ingredients_list[ingredient.get('id')] = (
                    ingredients_list.get('amount')
                )
            return data
        raise ValidationError('Рецепт не может быть без ингредиентов')

    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.save()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients_set = self.initial_data.get('ingredients')
        self.ingredient_recipe_create(ingredients_set, instance)
        return instance


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author',),
                message='Подписка невозможна'
            )
        ]

    def validate_following(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя!"
            )
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = '__all__'
