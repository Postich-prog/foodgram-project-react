from django.contrib.auth.models import AbstractUser
from django.db import models


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


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан'
    )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
        )
