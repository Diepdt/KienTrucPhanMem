from rest_framework import serializers
from .models import Cloth


class ClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = [
            'id', 'name', 'brand', 'sku', 'size', 'color', 'material',
            'price', 'stock', 'description', 'image_url', 'is_active',
            'created_by_staff_id', 'created_at'
        ]


class ClothCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = [
            'name', 'brand', 'sku', 'size', 'color', 'material',
            'price', 'stock', 'description', 'image_url'
        ]

    def validate_sku(self, value):
        if value == '' or value is None:
            return None
        return value
