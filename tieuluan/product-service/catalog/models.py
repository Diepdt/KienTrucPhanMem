from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=50, default='general', db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        unique_together = ('name', 'product_type')

    def __str__(self):
        return self.name


class Product(models.Model):
    """Unified product model for all current and future product types."""
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by_staff_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['product_type']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.product_type}:{self.name}"
