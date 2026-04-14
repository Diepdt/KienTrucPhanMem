from django.contrib import admin
from .models import Category, Product
admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'product_type', 'category', 'price', 'stock', 'is_active')
	list_filter = ('product_type', 'is_active', 'category')
	search_fields = ('name',)
