from django.contrib import admin
from .models import Mobile

@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'stock', 'os', 'processor', 'is_active')
    list_filter = ('brand', 'os', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'model', 'processor')
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'brand', 'model', 'color')}),
        ('Pricing & Stock', {'fields': ('price', 'stock')}),
        ('Specifications', {
            'fields': ('os', 'processor', 'ram', 'storage', 
                      'display_size', 'display_type', 'camera', 'battery')
        }),
        ('Category', {'fields': ('category_id', 'category_name')}),
        ('Description & Images', {'fields': ('description', 'image_url')}),
        ('Status', {'fields': ('is_active', 'created_by_staff_id')}),
    )
