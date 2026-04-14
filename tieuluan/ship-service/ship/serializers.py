from rest_framework import serializers
from .models import ShippingMethod, Shipment

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'cost', 'delivery_days', 'is_active']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'order_id', 'method', 'method_name', 'status',
                  'shipping_address', 'tracking_number', 'estimated_delivery',
                  'created_at', 'updated_at']
