from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('supplier', 'Поставщик'),
    )
    email = models.EmailField(unique=True, verbose_name='Email')
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='buyer',
        verbose_name='Тип пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.URLField(blank=True, null=True, verbose_name='Ссылка на магазин')
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shop',
        verbose_name='Пользователь-поставщик'
    )
    is_open = models.BooleanField(default=True, verbose_name='Принимает заказы')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name
