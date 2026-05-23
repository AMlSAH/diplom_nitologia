from rest_framework import serializers
from .models import Category, Product, ProductInfo

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')

class ProductInfoSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'shop', 'shop_name', 'external_id', 'price', 'quantity', 'parameters')

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    infos = ProductInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category', 'category_name', 'image', 'infos')

class ProductDetailSerializer(ProductListSerializer):
    pass
