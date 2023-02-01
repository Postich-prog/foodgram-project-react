from django.contrib.auth.models import AbstractUser
from django.db import models
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    CHOICES = [(USER, 'Пользователь'),
               (ADMIN, 'Администратор')]
    email = models.EmailField('Электронная почта',
                              max_length=254, unique=True)
    username = models.CharField('Логин пользователя',
                                unique=True, max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    role = models.CharField('Статус',
                            choices=CHOICES,
                            default=USER,
                            max_length=20)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff or self.role == User.ADMIN

    @property
    def is_block(self):
        return self.role == User.BLOCK

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


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
    """
    Ingredient Model
    """
    name = models.CharField('Имя', max_length=150, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=60)

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['-name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Recipe Model"""
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
    """
    Model of selected recipes
    """
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
    """
    Shopping List Model
    """
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
