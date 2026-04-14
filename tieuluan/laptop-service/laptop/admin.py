from django.contrib import admin
from .models import Laptop

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'stock', 'processor', 'ram', 'is_active')
    list_filter = ('brand', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'model', 'processor')
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'brand', 'model', 'color')}),
        ('Pricing & Stock', {'fields': ('price', 'stock')}),
        ('Specifications', {
            'fields': ('processor', 'ram', 'storage', 'display_size', 
                      'display_type', 'graphics', 'battery', 'weight')
        }),
        ('Category', {'fields': ('category_id', 'category_name')}),
        ('Description & Images', {'fields': ('description', 'image_url')}),
        ('Status', {'fields': ('is_active', 'created_by_staff_id')}),
    )
