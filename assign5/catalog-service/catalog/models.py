from django.db import models

class Category(models.Model):
    PRODUCT_TYPES = [
        ('book', 'Book'),
        ('cloth', 'Cloth'),
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES, default='book')
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        unique_together = ('name', 'product_type')

    def __str__(self):
        return self.name
