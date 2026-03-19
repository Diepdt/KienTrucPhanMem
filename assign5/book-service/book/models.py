from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category_id = models.IntegerField(null=True, blank=True)   # FK đến catalog-service
    category_name = models.CharField(max_length=255, blank=True)  # snapshot
    description = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by_staff_id = models.IntegerField(null=True, blank=True)  # Staff tạo sách
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
