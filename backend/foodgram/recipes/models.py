from django.contrib.auth.models import AbstractUser
from django.db import models
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


class User(AbstractUser):
    ROLE_CHOISE = [
        ('user', 'User'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
    ]

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False,
    )
    email = models.EmailField(
        'e-mail',
        max_length=254,
        unique=True,
        blank=False,
    )
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField(
        'Роль',
        default='user',
        choices=ROLE_CHOISE,
        max_length=10
    )
    first_name = models.CharField('Имя', max_length=150, blank=True,)
    last_name = models.CharField('Фамилия', max_length=150, blank=True,)
    confirmation_code = models.CharField(max_length=50, default="no code")

    class Meta:
        verbose_name = 'Польователь'
        verbose_name_plural = 'Польователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_confirmation_code(
        self,
        sender,
        instance=None,
        created=False,
        **kwards
    ):
        if created:
            confirmation_code = default_token_generator.make_token(
                instance
            )
            instance.confirmation_code = confirmation_code
            instance.save()


class Tag(models.Model):
    name = models.CharField('Имя', max_length=50, unique=True)
    color = ColorField('Цвет HEX', unique=True)
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['-name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField('Имя', max_length=150, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=60)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['-name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField('Имя', max_length=200, unique=True)
    image = models.ImageField('Изображение', upload_to='recipe/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(limit_value=1,
                    message="Введите число больше единицы")])

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipes',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField('Количество')

    def __str__(self):
        return f"Ингредиент: {self.ingredient}, Рецепт: {self.recipe}"

    class Meta():
        ordering = ['-id']
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='recipes_favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="favorites",
                               verbose_name='Рецепт')

    def __str__(self):
        return f'избранное пользователя {self.user}'

    class Meta():
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_carts',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'список покупок пользователя {self.user}'

    class Meta():
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_recording')


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    class Meta():
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(
            fields=['user', 'author'], name='unique_recording')
