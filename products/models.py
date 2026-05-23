from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategories',
        verbose_name='Родительская категория'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='infos',
        verbose_name='Товар'
    )
    shop = models.ForeignKey(
        'accounts.Shop',
        on_delete=models.CASCADE,
        related_name='product_infos',
        verbose_name='Магазин'
    )
    external_id = models.CharField(
        max_length=100,
        verbose_name='Внешний идентификатор (из прайса)',
        blank=True,
        null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Остаток')
    parameters = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Характеристики (настраиваемые поля)'
    )

    class Meta:
        unique_together = ('product', 'shop')
        verbose_name = 'Информация о товаре в магазине'
        verbose_name_plural = 'Информация о товарах'

    def __str__(self):
        return f"{self.product.name} @ {self.shop.name}"
