from django.db import models
from accounts.models import User
from products.models import ProductInfo


class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Пользователь'
    )
    full_address = models.TextField(verbose_name='Полный адрес')

    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f"{self.user.email}: {self.full_address[:50]}"


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f"Корзина {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        verbose_name='Товар (магазин)'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ('cart', 'product_info')

    def __str__(self):
        return f"{self.product_info.product.name} x{self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупатель'
    )
    delivery_address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Адрес доставки'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ #{self.id} – {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар (магазин)'
    )
    product_name = models.CharField(max_length=200, verbose_name='Название товара')
    shop_name = models.CharField(max_length=100, verbose_name='Название магазина')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
