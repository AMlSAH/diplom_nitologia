from rest_framework import serializers
from .models import Cart, CartItem, DeliveryAddress, Order, OrderItem
from products.models import ProductInfo
from products.serializers import ProductInfoSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)
    product_info_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(), write_only=True, source='product_info'
    )

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product_info', 'product_info_id', 'quantity')

    def validate(self, attrs):
        product_info = attrs.get('product_info')
        if product_info and not product_info.shop.is_open:
            raise serializers.ValidationError("Магазин не принимает заказы")
        return attrs

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_price')

    def get_total_price(self, obj):
        return sum(item.product_info.price * item.quantity for item in obj.items.all())

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ('id', 'user', 'full_address', 'phone')
        read_only_fields = ('user',)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'shop_name', 'price', 'quantity', 'total')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'delivery_address', 'status', 'created_at', 'items')
        read_only_fields = ('user', 'status', 'created_at')
