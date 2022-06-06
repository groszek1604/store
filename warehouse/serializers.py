from pydoc import describe
from rest_framework import serializers
from decimal import Decimal
from warehouse.models import Cart, Product, Collection, Review


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description'
                ,'inventory', 'price' ,'price_with_tax'
                ,'collection']

    price_with_tax = serializers.SerializerMethodField(
                                    method_name='calculate_tax')

    def calculate_tax(self, product):
        return product.price * Decimal(1.1)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['title', 'featured_product', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'items']