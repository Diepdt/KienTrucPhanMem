from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    item_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_type', 'product_id', 'product_name', 'product_subtitle',
            'product_image_url', 'product_snapshot',
            'price', 'quantity', 'item_total'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'shipping_method_id', 'shipping_method_name',
                  'shipping_cost', 'payment_method_id', 'payment_method_name',
                  'subtotal', 'total_amount', 'status', 'shipping_address',
                  'notes', 'items', 'created_at', 'updated_at']
