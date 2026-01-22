from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class UserAvatar(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='avatar',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to='users/avatar/',
        verbose_name='Аватар')

    class Meta:
        verbose_name_plural = 'Аватары'
        verbose_name = 'Аватар'


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
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'