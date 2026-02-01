from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F

from .constants import MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH,
        blank=False,
        null=False
    )
    avatar = models.ImageField(
        upload_to='users/avatar/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='some_name'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
