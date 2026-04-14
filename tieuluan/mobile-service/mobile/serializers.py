from rest_framework import serializers
from .models import Mobile

class MobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = ['id', 'name', 'brand', 'model', 'price', 'stock',
                  'category_id', 'category_name', 'os', 'processor', 'ram', 'storage',
                  'display_size', 'display_type', 'camera', 'battery', 'color',
                  'description', 'image_url', 'is_active', 
                  'created_by_staff_id', 'created_at']

class MobileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobile
        fields = ['name', 'brand', 'model', 'price', 'stock',
                  'category_id', 'os', 'processor', 'ram', 'storage',
                  'display_size', 'display_type', 'camera', 'battery', 'color',
                  'description', 'image_url']
