from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock',
                  'category_id', 'category_name', 'description',
                  'cover_url', 'is_active', 'created_by_staff_id', 'created_at']

class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'stock',
                  'category_id', 'description', 'cover_url']
