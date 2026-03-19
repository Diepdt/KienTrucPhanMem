from django.contrib import admin
from .models import Cloth


@admin.register(Cloth)
class ClothAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'price', 'stock', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'sku', 'color', 'size')
    list_filter = ('is_active', 'brand', 'size', 'color')
