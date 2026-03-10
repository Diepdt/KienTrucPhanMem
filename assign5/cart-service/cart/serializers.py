from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    item_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'book_title', 'book_author',
                  'price', 'quantity', 'item_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total', 'created_at', 'updated_at']
