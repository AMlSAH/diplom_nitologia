from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, DeliveryAddress, Order, OrderItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    DeliveryAddressSerializer,
    OrderSerializer,
)
from .permissions import IsSupplierForOrder
from products.models import ProductInfo
from orders.tasks import send_email_task


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_info_id = request.data.get('product_info_id')
        quantity = int(request.data.get('quantity', 1))

        product_info = get_object_or_404(ProductInfo, id=product_info_id)
        if not product_info.shop.is_open:
            return Response(
                {'detail': 'Магазин не принимает заказы'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    lookup_field = 'pk'


class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    lookup_field = 'pk'


class DeliveryAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeliveryAddressDeleteView(generics.DestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DeliveryAddress.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        if not cart.items.exists():
            return Response({'detail': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('delivery_address_id')
        if not address_id:
            return Response({'detail': 'Не указан адрес доставки'}, status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(DeliveryAddress, id=address_id, user=user)

        order = Order.objects.create(user=user, delivery_address=address)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_info=item.product_info,
                product_name=item.product_info.product.name,
                shop_name=item.product_info.shop.name,
                price=item.product_info.price,
                quantity=item.quantity,
                total=item.product_info.price * item.quantity
            )
        cart.items.all().delete()

        self.send_order_confirmation(order)
        self.send_invoice_to_admin(order)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def send_order_confirmation(self, order):
        items_text = "\n".join(
            [f"{item.product_name} x {item.quantity} = {item.total} руб."
             for item in order.items.all()]
        )
        message = (
            f"Ваш заказ №{order.id} принят.\n\n"
            f"Товары:\n{items_text}\n\n"
            f"Адрес доставки: {order.delivery_address.full_address}"
        )
        send_email_task.delay(
            subject='Подтверждение заказа',
            message=message,
            recipient_list=[order.user.email],
        )

    def send_invoice_to_admin(self, order):
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        items_text = "\n".join(
            [f"{item.product_name} x {item.quantity}" for item in order.items.all()]
        )
        message = (
            f"Накладная для заказа №{order.id}\n"
            f"Клиент: {order.user.email}\n"
            f"Товары:\n{items_text}\n"
            f"Адрес доставки: {order.delivery_address.full_address}"
        )
        send_email_task.delay(
            subject='Новая накладная',
            message=message,
            recipient_list=[admin_email],
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderListForStaffView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items')
        if user.user_type == 'supplier':
            shop = getattr(user, 'shop', None)
            if not shop:
                return Order.objects.none()
            return Order.objects.filter(
                items__product_info__shop=shop
            ).distinct().prefetch_related('items')
        return Order.objects.none()


class OrderStatusUpdateByStaffView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupplierForOrder]
    queryset = Order.objects.all()
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response({'detail': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = new_status
        instance.save()

        if old_status != new_status:
            self._notify_customer(instance, new_status)

        return Response(OrderSerializer(instance).data)

    def _notify_customer(self, order, new_status):
        status_display = dict(Order.STATUS_CHOICES).get(new_status, new_status)
        message = f"Статус вашего заказа №{order.id} изменён на «{status_display}»."
        send_email_task.delay(
            subject='Обновление статуса заказа',
            message=message,
            recipient_list=[order.user.email],
        )
