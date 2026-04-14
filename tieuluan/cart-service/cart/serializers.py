from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    item_total = serializers.ReadOnlyField()
    display_name = serializers.SerializerMethodField()
    display_subtitle = serializers.SerializerMethodField()
    display_image_url = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        return obj.product_name

    def get_display_subtitle(self, obj):
        return obj.product_subtitle

    def get_display_image_url(self, obj):
        return obj.product_image_url

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_type', 'product_id', 'product_name', 'product_subtitle',
            'product_image_url', 'source_service', 'product_snapshot',
            'display_name', 'display_subtitle', 'display_image_url',
            'price', 'quantity', 'item_total'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total', 'created_at', 'updated_at']
