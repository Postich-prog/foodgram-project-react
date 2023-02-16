import base64

from django.core.files.base import ContentFile
from recipes.models import Favorite, Ingredient, IngredientRecipe, Recipe, Tag
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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializers()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', 'amount'
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if type(ingredient.get('amount')) == str:
                if not ingredient.get('amount').isdigit():
                    raise serializers.ValidationError(
                        ('Количество ингредиента дольжно быть числом')
                    )
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Минимальное количество ингридиентов 1')
                )
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться.'
                )
            ingredients_set.add(id)
        data['ingredients'] = ingredients
        return data

    def add_tags_ingredients(self, instance, **validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        for tag in tags:
            instance.tags.add(tag)

        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredients_id=ingredient.get('id'),
                amount=ingredient.get('amount'))
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        recipe = super().create(validated_data)
        return self.add_tags_ingredients(
            recipe, ingredients=ingredients, tags=tags)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        instance = self.add_tags_ingredients(
            instance, ingredients=ingredients, tags=tags)
        return super().update(instance, validated_data)


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
