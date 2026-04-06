from django.db import models

class Laptop(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category_id = models.IntegerField(null=True, blank=True)   # FK đến catalog-service
    category_name = models.CharField(max_length=255, blank=True)  # snapshot
    
    # Laptop specific fields
    processor = models.CharField(max_length=100, blank=True)  # e.g., Intel Core i7
    ram = models.CharField(max_length=50, blank=True)  # e.g., 16GB DDR4
    storage = models.CharField(max_length=100, blank=True)  # e.g., 512GB SSD
    display_size = models.CharField(max_length=50, blank=True)  # e.g., 15.6 inches
    display_type = models.CharField(max_length=50, blank=True)  # e.g., IPS, OLED
    graphics = models.CharField(max_length=100, blank=True)  # e.g., NVIDIA RTX 4050
    battery = models.CharField(max_length=100, blank=True)  # e.g., 8700mAh
    weight = models.CharField(max_length=50, blank=True)  # e.g., 1.8kg
    color = models.CharField(max_length=50, blank=True)
    
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by_staff_id = models.IntegerField(null=True, blank=True)  # Staff tạo laptop
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}"
