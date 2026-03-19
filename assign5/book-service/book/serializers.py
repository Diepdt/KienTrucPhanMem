from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'price', 'stock',
                  'category_id', 'category_name', 'description',
                  'cover_url', 'is_active', 'created_by_staff_id', 'created_at']

class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'price', 'stock',
                  'category_id', 'description', 'cover_url']

    def validate_isbn(self, value):
        """Chuyển chuỗi rỗng thành None để tránh lỗi unique constraint."""
        if value == '' or value is None:
            return None
        return value
