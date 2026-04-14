from rest_framework import serializers
from .models import Laptop

class LaptopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laptop
        fields = ['id', 'name', 'brand', 'model', 'price', 'stock',
                  'category_id', 'category_name', 'processor', 'ram', 'storage',
                  'display_size', 'display_type', 'graphics', 'battery', 'weight',
                  'color', 'description', 'image_url', 'is_active', 
                  'created_by_staff_id', 'created_at']

class LaptopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laptop
        fields = ['name', 'brand', 'model', 'price', 'stock',
                  'category_id', 'processor', 'ram', 'storage',
                  'display_size', 'display_type', 'graphics', 'battery', 'weight',
                  'color', 'description', 'image_url']
