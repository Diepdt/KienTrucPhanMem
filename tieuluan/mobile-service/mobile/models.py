from django.db import models

class Mobile(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category_id = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=255, blank=True)
    
    # Mobile specific fields
    os = models.CharField(max_length=50, blank=True)  # iOS, Android
    processor = models.CharField(max_length=100, blank=True)  # e.g., Snapdragon 8 Gen 2
    ram = models.CharField(max_length=50, blank=True)  # e.g., 12GB
    storage = models.CharField(max_length=100, blank=True)  # e.g., 256GB
    display_size = models.CharField(max_length=50, blank=True)  # e.g., 6.7 inches
    display_type = models.CharField(max_length=50, blank=True)  # e.g., AMOLED
    camera = models.CharField(max_length=100, blank=True)  # e.g., 108MP
    battery = models.CharField(max_length=100, blank=True)  # e.g., 5000mAh
    color = models.CharField(max_length=50, blank=True)
    
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by_staff_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}"
